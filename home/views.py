# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.http import Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, HttpResponse, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from home.models import POST, Category, IMAGE_STORE
from datetime import datetime
from django.core.paginator import Paginator, PageNotAnInteger
from google.appengine.api import memcache
import json
from django.views.decorators.cache import cache_page
from django.db.models import Q
from home.function import MultiCookie
from google.appengine.ext import blobstore
from google.appengine.api import images
import cgi
now = datetime.now()

@cache_page(60 * 5)
def index(request, views=None):
	posts_list = None
	views_most = False
	comment_most = False
	lang = request.LANGUAGE_CODE
	if views is not None and views == "xem-nhieu":
		views_most = True
		posts_list = memcache.get('post-views')
		if posts_list is None:
			posts_list = POST.objects.all().order_by('-views')
			memcache.set('post-views', list(posts_list), 300)
	elif views is not None and views == "binh-luan-nhieu":
		comment_most = True
		posts_list = memcache.get('post-comments')
		if posts_list is None:
			posts_list = POST.objects.all().order_by('-comments')
			memcache.set('post-comments', list(posts_list), 300)
	else:
		posts_list = memcache.get('post-trang-chu')
		if posts_list is None:
			posts_list = POST.objects.all().order_by('-date')
			memcache.set('post-trang-chu', list(posts_list), 300)
	paginator = Paginator(posts_list, 5)
	posts = paginator.page(1)

	categories = memcache.get('categories-'+lang)
	if categories is None:
		categories = Category.objects.all().order_by('order')
		memcache.set('categories-'+lang, list(categories), 300)

	redirect = "/"

	if views_most == True:
		redirect = set_redirect(lang,"xem_nhieu")
	elif comment_most == True:
		redirect = set_redirect(lang,"binh_luan_nhieu")

	return render_to_response('home/index.html', {"redirect":redirect, "posts":posts, "categories":categories, "lang":lang}, context_instance=RequestContext(request))

def set_redirect(lang="vi", type_redirect_page=None, post=None, category=None):
	redirect = "/"
	if type_redirect_page == "xem_nhieu" and lang == "vi":
		return "/most-view/"
	elif type_redirect_page == "xem_nhieu" and lang == "en":
		return "/xem-nhieu/"
	elif type_redirect_page == "binh_luan_nhieu" and lang == "en":
		return "/binh-luan-nhieu/"
	elif type_redirect_page == "binh_luan_nhieu" and lang == "vi":
		return "/most-comment/"
	elif type_redirect_page == "detail" and lang == "en":
		return "/"+post.category.slug+"/"+post.slug+"/"
	elif type_redirect_page == "detail" and lang == "vi":
		return "/"+post.category.slug_en+"/"+post.slug_en+"/"
	elif type_redirect_page == "category" and lang == "en":
		return "/"+category.slug+"/"
	elif type_redirect_page == "category" and lang == "vi":
		return "/"+category.slug_en+"/"
	else:
		return redirect
		

def get_posts(request):
	if request.method == 'POST':
		category = None
		page = request.POST.get('page')

		if "category" in request.POST:
			category = request.POST["category"]
			if request.LANGUAGE_CODE == 'vi':
				cate= get_object_or_404(Category,slug=category)
			else:
				cate= get_object_or_404(Category,slug_en=category)
			posts_list = memcache.get('categories-%s' % category)
			if posts_list is None:
				posts_list = POST.objects.filter(category=cate).order_by('-date')
				memcache.set('categories-%s' % category, list(posts_list), 300)
		else:
			posts_list = memcache.get('post-trang-chu')
			if posts_list is None:
				posts_list = POST.objects.all().order_by('-date')

		paginator = Paginator(posts_list, 5)
		
		try:
			posts = paginator.page(page)
		except PageNotAnInteger:
			return HttpResponse(status=400)
		data = {"posts":posts, "lang":request.LANGUAGE_CODE}
		if category is not None:
			data["cate_current"] = category

		html = render_to_string("post/post_ajax.html", data)
		serialized_data = json.dumps({"html": html})
		return HttpResponse(serialized_data, mimetype='application/json')

	return HttpResponse(status=400)

def get_posts_detail_more(request):
	if request.method == 'POST':
		page = request.POST.get('page')
		typeGet = request.POST.get('type')
		category = request.POST["category"]
		cate= get_object_or_404(Category,slug=category)
		oldcookie = MultiCookie(cookie=request.COOKIES.get('viewed_post'))
		list_viewed = oldcookie.values
		if list_viewed is None:
			list_viewed = []
		if "viewed" == typeGet:
			posts_list = POST.objects.filter(pk__in=list_viewed,category=cate).order_by('-date')
		else:
			posts_list = POST.objects.filter(~Q(pk__in=list_viewed),category=cate).order_by('-date')

		paginator = Paginator(posts_list, 6)
		
		try:
			posts = paginator.page(page)
		except PageNotAnInteger:
			return HttpResponse(status=400)
		data = {"posts":posts, "type":typeGet, "lang":request.LANGUAGE_CODE}
		if category is not None:
			data["cate_current"] = category

		html = render_to_string("post/more_post_detail.html", data)
		serialized_data = json.dumps({"html": html})
		return HttpResponse(serialized_data, mimetype='application/json')

	return HttpResponse(status=400)

@cache_page(60 * 4)
def detail_post(request, category=None, slug=None):
	lang =  request.LANGUAGE_CODE
	if lang == 'vi':
		try:
			post = POST.objects.get(slug_en=slug)
		except:
			post = get_object_or_404(POST, slug=slug)
	else:
		try:
			post = POST.objects.get(slug=slug)
		except:
			post = get_object_or_404(POST, slug_en=slug)
	post.updateView()
	oldcookie = MultiCookie(cookie=request.COOKIES.get('viewed_post'))
	list_viewed = oldcookie.values
	if list_viewed is None:
		list_viewed = [post.id]
	else:
		if exits_in_array(list_viewed, post.id) == False:
			list_viewed.append(post.id)
	
	categories = Category.objects.all().order_by('order')

	redirect = set_redirect(lang, "detail", post)

	response = render_to_response('home/detail.html', {"redirect":redirect,"post":post,"categories":categories, "lang":lang}, context_instance=RequestContext(request))
	newcookie = MultiCookie(values=list_viewed)
	response.set_cookie('viewed_post',value=newcookie)

	return response

@cache_page(60 * 15)
def category(request, category=None):
	lang = request.LANGUAGE_CODE
	if lang == 'vi':
		try:
			cate= Category.objects.get(slug_en=category)
		except:	
			cate= get_object_or_404(Category,slug=category)
	else:
		try:
			cate= Category.objects.get(slug=category)
		except:
			cate= get_object_or_404(Category,slug_en=category)
	posts_list = memcache.get(category)
	if posts_list is None:		
		posts_list = POST.objects.filter(category=cate).order_by('-date')
		memcache.set(category, list(posts_list), 300) 
	paginator = Paginator(posts_list, 5)
	posts = paginator.page(1)

	categories = Category.objects.all().order_by('order')
	redirect = set_redirect(lang, "category", None, cate)
	return render_to_response('home/index.html', {"redirect": redirect ,"posts":posts,"categories":categories, "cate_current":cate,"lang":request.LANGUAGE_CODE}, context_instance=RequestContext(request))

def get_array_field(dict_list, field):
    arr_return = []
    for item in dict_list:
        arr_return.append(getattr(item, field))
    return arr_return

def exits_in_array(dict_list, ele):
    for item in dict_list:
        if item == ele:
        	return True
    return False


def category_post_relative(request, category=None):
	post=request.GET["post"]
	oldcookie = MultiCookie(cookie=request.COOKIES.get('viewed_post'))
	list_viewed = oldcookie.values
	if list_viewed is None:
		list_viewed = []
	
	if request.LANGUAGE_CODE == "vi":
		cate= get_object_or_404(Category,slug=category)
	else:
		cate= get_object_or_404(Category,slug_en=category)

	posts_list_not_view = POST.objects.filter(~Q(pk__in=list_viewed),category=cate).order_by('-date')

	posts_list__viewed = POST.objects.filter(pk__in=list_viewed,category=cate).order_by('-date')

	paginator = Paginator(posts_list_not_view, 6)
	posts_not_view = paginator.page(1)

	paginator_viewed = Paginator(posts_list__viewed, 6)
	posts_viewed = paginator_viewed.page(1)

	data = {"posts_not_view":posts_not_view, "posts_viewed":posts_viewed, "cate_current":category, "lang":request.LANGUAGE_CODE}
	html = render_to_string("post/post_relative_ajax.html", data)
	serialized_data = json.dumps({"html": html})

	return HttpResponse(serialized_data, mimetype='application/json')

@login_required
def upload_image(request):
	upload_files = get_uploads(request, field_name='file', populate_post=True)  # 'file' is file upload field in the form
	blob_info = upload_files[0]
	image = IMAGE_STORE()
	image.blob_key = blob_info.key()
	image.created_date = blob_info.creation
	image.size = blob_info.size
	image.file_name = blob_info.filename
	image.save()
	return redirect(request.POST["redirect"])

def get_uploads(request, field_name=None, populate_post=False):
    """Get uploads sent to this handler.
    Args:
      field_name: Only select uploads that were sent as a specific field.
      populate_post: Add the non blob fields to request.POST
    Returns:
      A list of BlobInfo records corresponding to each upload.
      Empty list if there are no blob-info records for field_name.
    """
 
    if hasattr(request,'__uploads') == False:
        request.META['wsgi.input'].seek(0)
        fields = cgi.FieldStorage(request.META['wsgi.input'], environ=request.META)
 
        request.__uploads = {}
        if populate_post:
            request.POST = {}
 
        for key in fields.keys():
            field = fields[key]
            if isinstance(field, cgi.FieldStorage) and 'blob-key' in field.type_options:
                request.__uploads.setdefault(key, []).append(blobstore.parse_blob_info(field))
            elif populate_post:
                request.POST[key] = field.value
    if field_name:
        try:
            return list(request.__uploads[field_name])
        except KeyError:
            return []
    else:
        results = []
        for uploads in request.__uploads.itervalues():
            results += uploads
        return results

@login_required
def get_images(request):
	images_list = IMAGE_STORE.objects.all().order_by('-created_date')
	paginator = Paginator(images_list, 6)
	imagesPage = paginator.page(1)
	urls = []
	for blob in imagesPage:
		urls.append(images.get_serving_url(blob.blob_key))
	data = {"urls" : urls, "images":imagesPage}
	html = render_to_string("image/image_ajax.html", data)
	serialized_data = json.dumps({"html": html})
	return HttpResponse(serialized_data, mimetype='application/json')

@login_required
def get_images_more(request):
	if request.method == 'POST':
		page = request.POST.get('page')
		images_list = IMAGE_STORE.objects.all().order_by('-created_date')
		paginator = Paginator(images_list, 6)
		try:
			imagesPage = paginator.page(page)
		except PageNotAnInteger:
			return HttpResponse(status=400)
		urls = []
		for blob in imagesPage:
			urls.append(images.get_serving_url(blob.blob_key))
		data = {"urls" : urls, "images":imagesPage}
		html = render_to_string("image/image_ajax.html", data)
		serialized_data = json.dumps({"html": html})
		return HttpResponse(serialized_data, mimetype='application/json')

	return HttpResponse(status=400)

def commented(request):
	if request.method == "POST":
		post = get_object_or_404(POST, pk=request.POST["p"])
		if "type" in request.POST:
			post.updateComment("removed")
		else:
			post.updateComment()
		return HttpResponse(status=200)
	return HttpResponse(status=400)

def liked(request):
	if request.method == "POST":
		post = get_object_or_404(POST, pk=request.POST["p"])
		if "type" in request.POST:
			post.updateLike("unliked")
		else:
			post.updateLike()
		return HttpResponse(status=200)
	return HttpResponse(status=400)