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
now = datetime.now()
from google.appengine.api import memcache
import json
from django.views.decorators.cache import cache_page

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

	categories = memcache.get('categories')
	if categories is None:
		categories = Category.objects.all().order_by('order')
		memcache.set('categories', list(categories), 300)

	return render_to_response('home/index.html', {"posts":posts, "categories":categories}, context_instance=RequestContext(request))

@login_required(login_url='/accounts/login/')
def create_post(request):
	if request.method == 'POST':
		post = POST()
		post.content = request.POST.get('link')
		post.author = request.user
		post.date = now
		post.save()
	return HttpResponseRedirect('/')

def get_posts(request):
	if request.method == 'POST':
		category = None
		page = request.POST.get('page')

		if "category" in request.POST:
			category = request.POST["category"]
			cate= get_object_or_404(Category,slug=category)
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
		data = {"posts":posts}
		if category is not None:
			data["cate_current"] = category

		html = render_to_string("post/post_ajax.html", data)
		serialized_data = json.dumps({"html": html})
		return HttpResponse(serialized_data, mimetype='application/json')

	return HttpResponse(status=400)

@cache_page(60 * 4)
def detail_post(request, category=None, slug=None):
	posts_list = memcache.get('post-trang-chu')
	if posts_list is not None:
		memcache.delete("post-trang-chu")

	post = get_object_or_404(POST, slug=slug)

	post.updateView()
	categories = Category.objects.all().order_by('order')
	return render_to_response('home/detail.html', {"post":post,"categories":categories}, context_instance=RequestContext(request))

@cache_page(60 * 15)
def category(request, category=None):
	cate= get_object_or_404(Category,slug=category)
	posts_list = memcache.get(category)
	if posts_list is None:		
		posts_list = POST.objects.filter(category=cate).order_by('-date')
		memcache.set(category, list(posts_list), 300) 
	paginator = Paginator(posts_list, 5)
	posts = paginator.page(1)

	categories = Category.objects.all().order_by('order')
	return render_to_response('home/index.html', {"posts":posts,"categories":categories, "cate_current":cate}, context_instance=RequestContext(request))