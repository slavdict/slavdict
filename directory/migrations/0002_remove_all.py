# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Category'
        db.delete_table('directory_category')

        # Deleting model 'TagLibrary'
        db.delete_table('directory_taglibrary')

        # Deleting model 'CategoryTag'
        db.delete_table('directory_categorytag')

        # Deleting model 'ValueTag'
        db.delete_table('directory_valuetag')

        # Deleting model 'CategoryValue'
        db.delete_table('directory_categoryvalue')


    def backwards(self, orm):
        # Adding model 'Category'
        db.create_table('directory_category', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('directory', ['Category'])

        # Adding model 'TagLibrary'
        db.create_table('directory_taglibrary', (
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('directory', ['TagLibrary'])

        # Adding model 'CategoryTag'
        db.create_table('directory_categorytag', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.Category'])),
            ('taglib', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.TagLibrary'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('directory', ['CategoryTag'])

        # Adding model 'ValueTag'
        db.create_table('directory_valuetag', (
            ('pinned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('catvalue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.CategoryValue'])),
            ('css_class2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('taglib', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.TagLibrary'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('directory', ['ValueTag'])

        # Adding model 'CategoryValue'
        db.create_table('directory_categoryvalue', (
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.Category'])),
            ('pinned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('css_class2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('directory', ['CategoryValue'])


    models = {
        
    }

    complete_apps = ['directory']