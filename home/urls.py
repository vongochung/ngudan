from django.conf.urls import *

urlpatterns = patterns('home.views',
   url(r'^$', 'index'),
   url(r'^get-posts/$', 'get_posts'),
   url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/$', 'detail_post', name="detail_post"),
   url(r'^(?P<category>[-\w]+)/$', 'category', name='list_post_category'),
)
