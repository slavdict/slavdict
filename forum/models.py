# -*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    
    supercategory = models.ForeignKey('self', null=True, blank=True, related_name='subcategories')
    title         = models.CharField(max_length=100)
    description   = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.title


class Topic(models.Model):

    title       = models.CharField(max_length=100)
    category    = models.ForeignKey(Category, related_name='topics')
    user        = models.ForeignKey(User, related_name='topics')
    started_at  = models.DateTimeField(editable=False)

    # Administration
    pinned = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    @property
    def post_count(self):
        return self.posts.count()
    
    @property
    def last_post(self):
        return self.posts.order_by('-posted_at')[0]
    
    @property
    def last_post_at(self):
        return self.last_post.edited_at
    
    @property
    def last_user_name(self):
        return self.last_post.user

    def __unicode__(self):
        return self.title


class Post(models.Model):

    user      = models.ForeignKey(User, related_name='posts')
    topic     = models.ForeignKey(Topic, related_name='posts')
    text      = models.TextField()
    posted_at = models.DateTimeField(editable=False, auto_now_add=True)
    edited_at = models.DateTimeField(editable=False, null=True, blank=True, auto_now=True)

    # Administration
    hidden = models.BooleanField(default=False)

    def __unicode__(self):
        return '%s -- %s' % (self.topic.id, self.posted_at)
