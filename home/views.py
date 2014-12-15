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

def index(request):
	posts_list = POST.objects.all().order_by('-date')
	paginator = Paginator(posts_list, 5)
	posts = paginator.page(1)
	return render_to_response('home/index.html', {"posts":posts}, context_instance=RequestContext(request))

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
		posts_list = POST.objects.all().order_by('-date')
		paginator = Paginator(posts_list, 5)
		page = request.POST.get('page')
		try:
			posts = paginator.page(page)
		except PageNotAnInteger:
			return HttpResponse(status=400)
		return render_to_response('post/post_ajax.html', {"posts":posts}, context_instance=RequestContext(request))

	return HttpResponse(status=400)

def detail_post(request, category=None, slug=None):
	post = get_object_or_404(POST, slug=slug)
	return render_to_response('home/detail.html', {"post":post}, context_instance=RequestContext(request))

def category(request, category=None):
	cate= get_object_or_404(Category,slug=category)
	posts_list = POST.objects.filter(category=cate).order_by('-date')
	paginator = Paginator(posts_list, 5)
	posts = paginator.page(1)
	return render_to_response('home/index.html', {"posts":posts, "category":cate}, context_instance=RequestContext(request))