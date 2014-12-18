from django.conf.urls import *

urlpatterns = patterns('home.views',
   url(r'^$', 'index', name="index"),
   url(r'^xem-nhieu/$', 'index', {'views': 'xem-nhieu'}),
   url(r'^binh-luan-nhieu/$', 'index', {'views': 'binh-luan-nhieu'}),
   url(r'^get-posts/$', 'get_posts'),
   url(r'^(?P<category>[-\w]+)/(?P<slug>[-\w]+)/$', 'detail_post', name="detail_post"),
   url(r'^(?P<category>[-\w]+)/$', 'category', name='list_post_category'),
)
