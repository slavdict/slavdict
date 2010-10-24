# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('directory_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('directory', ['Category'])

        # Adding model 'CategoryValue'
        db.create_table('directory_categoryvalue', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.Category'])),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.PositiveSmallIntegerField')(null=True, blank=True)),
            ('pinned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('css_class2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('directory', ['CategoryValue'])

        # Adding model 'TagLibrary'
        db.create_table('directory_taglibrary', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('slug', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('directory', ['TagLibrary'])

        # Adding model 'CategoryTag'
        db.create_table('directory_categorytag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('taglib', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.TagLibrary'])),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.Category'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=60)),
        ))
        db.send_create_signal('directory', ['CategoryTag'])

        # Adding model 'ValueTag'
        db.create_table('directory_valuetag', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('taglib', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.TagLibrary'])),
            ('catvalue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.CategoryValue'])),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('pinned', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('css_class', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('css_class2', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal('directory', ['ValueTag'])


    def backwards(self, orm):
        
        # Deleting model 'Category'
        db.delete_table('directory_category')

        # Deleting model 'CategoryValue'
        db.delete_table('directory_categoryvalue')

        # Deleting model 'TagLibrary'
        db.delete_table('directory_taglibrary')

        # Deleting model 'CategoryTag'
        db.delete_table('directory_categorytag')

        # Deleting model 'ValueTag'
        db.delete_table('directory_valuetag')


    models = {
        'directory.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'directory.categorytag': {
            'Meta': {'object_name': 'CategoryTag'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'taglib': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.TagLibrary']"})
        },
        'directory.categoryvalue': {
            'Meta': {'ordering': "('category', 'order', 'id')", 'object_name': 'CategoryValue'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.Category']"}),
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'css_class2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.PositiveSmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pinned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'directory.taglibrary': {
            'Meta': {'ordering': "('slug',)", 'object_name': 'TagLibrary'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'directory.valuetag': {
            'Meta': {'ordering': "('taglib', 'catvalue', 'catvalue__order')", 'object_name': 'ValueTag'},
            'catvalue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.CategoryValue']"}),
            'css_class': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'css_class2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'pinned': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'taglib': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.TagLibrary']"})
        }
    }

    complete_apps = ['directory']
