# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.contrib import admin
import dbindexer
from django.conf.urls import patterns, include, url

handler500 = 'djangotoolbox.errorviews.server_error'

# django admin
admin.autodiscover()
# search for dbindexes.py in all INSTALLED_APPS and load them
dbindexer.autodiscover()

urlpatterns = patterns('',
	('^admin-ngudan/', include(admin.site.urls)),
	(r'^i18n/', include('django.conf.urls.i18n')),
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog'),
    ('^_ah/warmup$', 'djangoappengine.views.warmup'),
    (r'^mce_filebrowser/', include('mce_filebrowser.urls')),
    (r'^tinymce/', include('tinymce.urls')),
    (r'', include('home.urls')),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {"template_name":"home/login.html"}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout', {"next_page" : "/"}),
    

)
