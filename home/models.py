from django.db import models
from django.contrib.auth.models import User
import pytz
from pytz import timezone
import datetime
from django.core.paginator import Paginator, PageNotAnInteger

from django.template.defaultfilters import slugify
from google.appengine.api import memcache

class UtcTzinfo(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    def dst(self, dt):
        return datetime.timedelta(0)

    def tzname(self, dt):
        return 'UTC'

    def olsen_name(self):
        return 'UTC'


TZINFOS = {
    'utc': UtcTzinfo(),
}



class Category(models.Model):
    name = models.CharField(max_length=135, unique=True, null=True)
    slug = models.SlugField(blank=False, max_length=255, unique=True)
    parent_id = models.ForeignKey('self', null=True, blank=True)
    order = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_category(self, category_id=None):
        categories = Category.objects.filter(parent_id=category_id)
        return categories

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if memcache.get('categories') is not None:
            memcache.delete('categories')
        super(Category, self).save(*args, **kwargs)


class POST(models.Model):
    category = models.ForeignKey(Category, null=False, related_name='page_category')
    author = models.ForeignKey(User)
    title = models.CharField(max_length=235, unique=True, null=True)
    slug = models.SlugField(blank=False, max_length=255, unique=True)
    description = models.TextField()
    link = models.TextField(null=True,blank=True)
    start = models.IntegerField(null=True,blank=True)
    end = models.IntegerField(null=True,blank=True)
    views = models.IntegerField(null=True,blank=True,default=0)
    likes = models.IntegerField(null=True,blank=True,default=0)
    comments = models.IntegerField(null=True,blank=True,default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' % self.title

    def updateView(self):
        if self.views is None:
            self.views = 1
        else:
            self.views = self.views + 1
        self.save()

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        self.link = self.link.replace("https://www.youtube.com/watch?v=", "");
        if memcache.get('post-trang-chu') is not None:
            memcache.delete('post-trang-chu')

        if memcache.get(self.category.slug) is not None:
            memcache.delete(self.category.slug)
            
        super(POST, self).save(*args, **kwargs)


    def translate(self):
        utc = TZINFOS['utc']
        self.date = self.date.replace(tzinfo=utc)
        return self.date.astimezone(pytz.timezone('Asia/Ho_Chi_Minh'))