# -*- coding: UTF-8 -*-

from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):

    title       = models.CharField(max_length=100)
    forum       = models.ForeignKey(Forum, related_name='topics')
    user        = models.ForeignKey(User, related_name='topics')
    description = models.CharField(max_length=100, blank=True)
    started_at  = models.DateTimeField(editable=False)

    # Administration
    pinned = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    # Denormalised data
    post_count     = models.PositiveIntegerField(default=0)
    metapost_count = models.PositiveIntegerField(default=0)
    view_count     = models.PositiveIntegerField(default=0)
    last_post_at   = models.DateTimeField(null=True, blank=True)
    last_user_id   = models.PositiveIntegerField(null=True, blank=True)
    last_username  = models.CharField(max_length=30, blank=True)

    objects = TopicManager()

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
