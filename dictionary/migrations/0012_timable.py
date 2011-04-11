# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Example.mtime'
        db.add_column('dictionary_example', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'Example.muser'
        db.add_column('dictionary_example', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'GreekEquivalentForMeaning.mtime'
        db.add_column('dictionary_greekequivalentformeaning', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'GreekEquivalentForMeaning.muser'
        db.add_column('dictionary_greekequivalentformeaning', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'Etymology.mtime'
        db.add_column('dictionary_etymology', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'Etymology.muser'
        db.add_column('dictionary_etymology', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'MeaningContext.mtime'
        db.add_column('dictionary_meaningcontext', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'MeaningContext.muser'
        db.add_column('dictionary_meaningcontext', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'CollocationGroup.ctime'
        db.add_column('dictionary_collocationgroup', 'ctime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True), keep_default=False)

        # Adding field 'CollocationGroup.cuser'
        db.add_column('dictionary_collocationgroup', 'cuser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='cuser_collocationgroup_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'CollocationGroup.mtime'
        db.add_column('dictionary_collocationgroup', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'CollocationGroup.muser'
        db.add_column('dictionary_collocationgroup', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='muser_collocationgroup_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'SynonymGroup.ctime'
        db.add_column('dictionary_synonymgroup', 'ctime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True), keep_default=False)

        # Adding field 'SynonymGroup.cuser'
        db.add_column('dictionary_synonymgroup', 'cuser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='cuser_synonymgroup_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'SynonymGroup.mtime'
        db.add_column('dictionary_synonymgroup', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'SynonymGroup.muser'
        db.add_column('dictionary_synonymgroup', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='muser_synonymgroup_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'Entry.mtime'
        db.add_column('dictionary_entry', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'Entry.muser'
        db.add_column('dictionary_entry', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='muser_entry_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'Entry.ctime'
        db.add_column('dictionary_entry', 'ctime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True), keep_default=False)

        # Adding field 'Entry.cuser'
        db.add_column('dictionary_entry', 'cuser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='cuser_entry_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Changing field 'Entry.status'
        db.alter_column('dictionary_entry', 'status_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['directory.CategoryValue']))

        # Adding field 'GreekEquivalentForExample.mtime'
        db.add_column('dictionary_greekequivalentforexample', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'GreekEquivalentForExample.muser'
        db.add_column('dictionary_greekequivalentforexample', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'Meaning.ctime'
        db.add_column('dictionary_meaning', 'ctime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now_add=True, blank=True), keep_default=False)

        # Adding field 'Meaning.cuser'
        db.add_column('dictionary_meaning', 'cuser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='cuser_meaning_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'Meaning.mtime'
        db.add_column('dictionary_meaning', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'Meaning.muser'
        db.add_column('dictionary_meaning', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, related_name='muser_meaning_set', to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'OrthographicVariant.mtime'
        db.add_column('dictionary_orthographicvariant', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'OrthographicVariant.muser'
        db.add_column('dictionary_orthographicvariant', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_user.CustomUser']), keep_default=False)

        # Adding field 'Collocation.mtime'
        db.add_column('dictionary_collocation', 'mtime', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, auto_now=True, blank=True), keep_default=False)

        # Adding field 'Collocation.muser'
        db.add_column('dictionary_collocation', 'muser', self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['custom_user.CustomUser']), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Example.mtime'
        db.delete_column('dictionary_example', 'mtime')

        # Deleting field 'Example.muser'
        db.delete_column('dictionary_example', 'muser_id')

        # Deleting field 'GreekEquivalentForMeaning.mtime'
        db.delete_column('dictionary_greekequivalentformeaning', 'mtime')

        # Deleting field 'GreekEquivalentForMeaning.muser'
        db.delete_column('dictionary_greekequivalentformeaning', 'muser_id')

        # Deleting field 'Etymology.mtime'
        db.delete_column('dictionary_etymology', 'mtime')

        # Deleting field 'Etymology.muser'
        db.delete_column('dictionary_etymology', 'muser_id')

        # Deleting field 'MeaningContext.mtime'
        db.delete_column('dictionary_meaningcontext', 'mtime')

        # Deleting field 'MeaningContext.muser'
        db.delete_column('dictionary_meaningcontext', 'muser_id')

        # Deleting field 'CollocationGroup.ctime'
        db.delete_column('dictionary_collocationgroup', 'ctime')

        # Deleting field 'CollocationGroup.cuser'
        db.delete_column('dictionary_collocationgroup', 'cuser_id')

        # Deleting field 'CollocationGroup.mtime'
        db.delete_column('dictionary_collocationgroup', 'mtime')

        # Deleting field 'CollocationGroup.muser'
        db.delete_column('dictionary_collocationgroup', 'muser_id')

        # Deleting field 'SynonymGroup.ctime'
        db.delete_column('dictionary_synonymgroup', 'ctime')

        # Deleting field 'SynonymGroup.cuser'
        db.delete_column('dictionary_synonymgroup', 'cuser_id')

        # Deleting field 'SynonymGroup.mtime'
        db.delete_column('dictionary_synonymgroup', 'mtime')

        # Deleting field 'SynonymGroup.muser'
        db.delete_column('dictionary_synonymgroup', 'muser_id')

        # Deleting field 'Entry.mtime'
        db.delete_column('dictionary_entry', 'mtime')

        # Deleting field 'Entry.muser'
        db.delete_column('dictionary_entry', 'muser_id')

        # Deleting field 'Entry.ctime'
        db.delete_column('dictionary_entry', 'ctime')

        # Deleting field 'Entry.cuser'
        db.delete_column('dictionary_entry', 'cuser_id')

        # Changing field 'Entry.status'
        db.alter_column('dictionary_entry', 'status_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.CategoryValue']))

        # Deleting field 'GreekEquivalentForExample.mtime'
        db.delete_column('dictionary_greekequivalentforexample', 'mtime')

        # Deleting field 'GreekEquivalentForExample.muser'
        db.delete_column('dictionary_greekequivalentforexample', 'muser_id')

        # Deleting field 'Meaning.ctime'
        db.delete_column('dictionary_meaning', 'ctime')

        # Deleting field 'Meaning.cuser'
        db.delete_column('dictionary_meaning', 'cuser_id')

        # Deleting field 'Meaning.mtime'
        db.delete_column('dictionary_meaning', 'mtime')

        # Deleting field 'Meaning.muser'
        db.delete_column('dictionary_meaning', 'muser_id')

        # Deleting field 'OrthographicVariant.mtime'
        db.delete_column('dictionary_orthographicvariant', 'mtime')

        # Deleting field 'OrthographicVariant.muser'
        db.delete_column('dictionary_orthographicvariant', 'muser_id')

        # Deleting field 'Collocation.mtime'
        db.delete_column('dictionary_collocation', 'mtime')

        # Deleting field 'Collocation.muser'
        db.delete_column('dictionary_collocation', 'muser_id')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'custom_user.customuser': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'object_name': 'CustomUser', '_ormbases': ['auth.User']},
            'second_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        'dictionary.collocation': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Collocation'},
            'civil_equivalent': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'collocation': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'collogroup': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.CollocationGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']"}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dictionary.collocationgroup': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'CollocationGroup'},
            'base_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collocationgroup_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'base_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collocationgroup_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_collogroup_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_collogroup_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Meaning']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cuser_collocationgroup_set'", 'to': "orm['custom_user.CustomUser']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_collogroup_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_collogroup_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'muser_collocationgroup_set'", 'to': "orm['custom_user.CustomUser']"})
        },
        'dictionary.entry': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Entry'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'antconc_query': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'canonical_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cf_collogroups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.CollocationGroup']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Meaning']"}),
            'civil_equivalent': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cuser_entry_set'", 'to': "orm['custom_user.CustomUser']"}),
            'derivation_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'derived_entry_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'editor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entries_of_gender'", 'null': 'True', 'to': "orm['directory.CategoryValue']"}),
            'genitive': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'grequiv_status': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'homonym_gloss': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'homonym_order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_collogroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_entry_set'", 'null': 'True', 'to': "orm['dictionary.CollocationGroup']"}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_entry_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_entry_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'muser_entry_set'", 'to': "orm['custom_user.CustomUser']"}),
            'nom_pl': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'nom_sg': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'onym': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.CategoryValue']", 'null': 'True', 'blank': 'True'}),
            'part_of_speech': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries_of_pos'", 'to': "orm['directory.CategoryValue']"}),
            'participle_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entries_of_parttype'", 'null': 'True', 'to': "orm['directory.CategoryValue']"}),
            'percent_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'possessive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sg1': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'sg2': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'short_form': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entries_of_status'", 'null': 'True', 'to': "orm['directory.CategoryValue']"}),
            'tantum': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entries_of_tantum'", 'null': 'True', 'to': "orm['directory.CategoryValue']"}),
            'transitivity': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entries_of_transitivity'", 'null': 'True', 'to': "orm['directory.CategoryValue']"}),
            'uninflected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'word_forms_list': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'dictionary.etymology': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Etymology'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'collocation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Collocation']", 'null': 'True', 'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Entry']", 'null': 'True', 'blank': 'True'}),
            'etymon_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'etymon_set'", 'null': 'True', 'to': "orm['dictionary.Etymology']"}),
            'gloss': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.CategoryValue']"}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'meaning': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']"}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'questionable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'translit': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'unclear': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'dictionary.example': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Example'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'address_text': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'context': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'example': ('django.db.models.fields.TextField', [], {}),
            'greek_eq_status': ('django.db.models.fields.CharField', [], {'default': "u'L'", 'max_length': '1'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meaning': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']"}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dictionary.greekequivalentforexample': {
            'Meta': {'object_name': 'GreekEquivalentForExample'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'for_example': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Example']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']"}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dictionary.greekequivalentformeaning': {
            'Meta': {'object_name': 'GreekEquivalentForMeaning'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'for_meaning': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Meaning']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'dictionary.meaning': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Meaning'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cf_collogroups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_meaning_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.CollocationGroup']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_meaning_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_meaning_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Meaning']"}),
            'collogroup_container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meaning_set'", 'null': 'True', 'to': "orm['dictionary.CollocationGroup']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cuser_meaning_set'", 'to': "orm['custom_user.CustomUser']"}),
            'entry_container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meaning_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'gloss': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_collogroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': "orm['dictionary.CollocationGroup']"}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'meaning': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'metaphorical': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'muser_meaning_set'", 'to': "orm['custom_user.CustomUser']"}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parent_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_meaning_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'substantivus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'substantivus_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.CategoryValue']", 'null': 'True', 'blank': 'True'})
        },
        'dictionary.meaningcontext': {
            'Meta': {'object_name': 'MeaningContext'},
            'context': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_text': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'meaning': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']"}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'right_text': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'})
        },
        'dictionary.orthographicvariant': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'OrthographicVariant'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orthographic_variants'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'frequency': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idem': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_reconstructed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['custom_user.CustomUser']"}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dictionary.synonymgroup': {
            'Meta': {'object_name': 'SynonymGroup'},
            'base': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'base_synonym_in'", 'to': "orm['dictionary.Entry']"}),
            'collogroup_synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['dictionary.CollocationGroup']", 'null': 'True', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'cuser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cuser_synonymgroup_set'", 'to': "orm['custom_user.CustomUser']"}),
            'entry_synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'synonym_in'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now': 'True', 'blank': 'True'}),
            'muser': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'muser_synonymgroup_set'", 'to': "orm['custom_user.CustomUser']"})
        },
        'directory.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'slug': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
        }
    }

    complete_apps = ['dictionary']
