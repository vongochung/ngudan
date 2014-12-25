# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from django.http import Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, redirect, HttpResponse, get_object_or_404
from django.template import RequestContext
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from home.models import POST, Category
from datetime import datetime
from django.core.paginator import Paginator, PageNotAnInteger
from google.appengine.api import memcache
import json
from django.views.decorators.cache import cache_page
from django.db.models import Q
from home.function import MultiCookie
now = datetime.now()

@cache_page(60 * 3)
def index(request, views=None):
	posts_list = None
	if views is not None and views == "xem-nhieu":
		posts_list = memcache.get('post-views')
		if posts_list is None:
			posts_list = POST.objects.all().order_by('-views')
			memcache.set('post-views', list(posts_list), 300)
	elif views is not None and views == "binh-luan-nhieu":
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

	categories = memcache.get('categories-'+request.LANGUAGE_CODE)
	if categories is None:
		categories = Category.objects.all().order_by('order')
		memcache.set('categories-'+request.LANGUAGE_CODE, list(categories), 300)

	return render_to_response('home/index.html', {"posts":posts, "categories":categories, "lang":request.LANGUAGE_CODE}, context_instance=RequestContext(request))


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
	if request.LANGUAGE_CODE == 'vi':
		post = get_object_or_404(POST, slug=slug)
	else:
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
	response = render_to_response('home/detail.html', {"post":post,"categories":categories, "lang":request.LANGUAGE_CODE}, context_instance=RequestContext(request))
	newcookie = MultiCookie(values=list_viewed)
	response.set_cookie('viewed_post',value=newcookie)

	return response

@cache_page(60 * 15)
def category(request, category=None):
	if request.LANGUAGE_CODE == 'vi':
		cate= get_object_or_404(Category,slug=category)
	else:
		cate= get_object_or_404(Category,slug_en=category)
	posts_list = memcache.get(category)
	if posts_list is None:		
		posts_list = POST.objects.filter(category=cate).order_by('-date')
		memcache.set(category, list(posts_list), 300) 
	paginator = Paginator(posts_list, 5)
	posts = paginator.page(1)

	categories = Category.objects.all().order_by('order')
	return render_to_response('home/index.html', {"posts":posts,"categories":categories, "cate_current":cate,"lang":request.LANGUAGE_CODE}, context_instance=RequestContext(request))

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