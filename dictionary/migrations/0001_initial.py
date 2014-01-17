# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Entry'
        db.create_table(u'dictionary_entry', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('civil_equivalent', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('reconstructed_headword', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('questionable_headword', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('homonym_order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('homonym_gloss', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('duplicate', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('part_of_speech', self.gf('django.db.models.fields.CharField')(default='', max_length=1)),
            ('uninflected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('word_forms_list', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tantum', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True)),
            ('gender', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True)),
            ('genitive', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('onym', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True)),
            ('canonical_name', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nom_sg', self.gf('django.db.models.fields.CharField')(default='', max_length=25, blank=True)),
            ('short_form', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('possessive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('transitivity', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True)),
            ('sg1', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('sg2', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('participle_type', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True)),
            ('derivation_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='derived_entry_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_entry_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_collogroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_entry_set', null=True, to=orm['dictionary.CollocationGroup'])),
            ('link_to_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_entry_set', null=True, to=orm['dictionary.Meaning'])),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='c', max_length=1)),
            ('percent_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('antconc_query', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')()),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('good', self.gf('django.db.models.fields.TextField')(default=u'b', max_length=1)),
        ))
        db.send_create_signal(u'dictionary', ['Entry'])

        # Adding M2M table for field cf_entries on 'Entry'
        m2m_table_name = db.shorten_name(u'dictionary_entry_cf_entries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_entry', models.ForeignKey(orm[u'dictionary.entry'], null=False)),
            ('to_entry', models.ForeignKey(orm[u'dictionary.entry'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_entry_id', 'to_entry_id'])

        # Adding M2M table for field cf_collogroups on 'Entry'
        m2m_table_name = db.shorten_name(u'dictionary_entry_cf_collogroups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm[u'dictionary.entry'], null=False)),
            ('collocationgroup', models.ForeignKey(orm[u'dictionary.collocationgroup'], null=False))
        ))
        db.create_unique(m2m_table_name, ['entry_id', 'collocationgroup_id'])

        # Adding M2M table for field cf_meanings on 'Entry'
        m2m_table_name = db.shorten_name(u'dictionary_entry_cf_meanings')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm[u'dictionary.entry'], null=False)),
            ('meaning', models.ForeignKey(orm[u'dictionary.meaning'], null=False))
        ))
        db.create_unique(m2m_table_name, ['entry_id', 'meaning_id'])

        # Adding M2M table for field authors on 'Entry'
        m2m_table_name = db.shorten_name(u'dictionary_entry_authors')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm[u'dictionary.entry'], null=False)),
            ('customuser', models.ForeignKey(orm[u'custom_user.customuser'], null=False))
        ))
        db.create_unique(m2m_table_name, ['entry_id', 'customuser_id'])

        # Adding model 'Etymology'
        db.create_table(u'dictionary_etymology', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Entry'], null=True, blank=True)),
            ('collocation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Collocation'], null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('etymon_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='etymon_set', null=True, to=orm['dictionary.Etymology'])),
            ('language', self.gf('django.db.models.fields.CharField')(default='', max_length=1)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('unitext', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('translit', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('meaning', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('gloss', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('unclear', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('questionable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mark', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('corrupted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['Etymology'])

        # Adding model 'MeaningContext'
        db.create_table(u'dictionary_meaningcontext', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meaning', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Meaning'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('left_text', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('context', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('right_text', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['MeaningContext'])

        # Adding model 'Meaning'
        db.create_table(u'dictionary_meaning', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry_container', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='meaning_set', null=True, to=orm['dictionary.Entry'])),
            ('collogroup_container', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='meaning_set', null=True, to=orm['dictionary.CollocationGroup'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=345, blank=True)),
            ('parent_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_meaning_set', null=True, to=orm['dictionary.Meaning'])),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('link_to_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_meaning_set', null=True, to=orm['dictionary.Meaning'])),
            ('link_to_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_meaning_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_collogroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_meaning_set', null=True, to=orm['dictionary.CollocationGroup'])),
            ('metaphorical', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('meaning', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('gloss', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('substantivus', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('substantivus_type', self.gf('django.db.models.fields.CharField')(default='', max_length=1, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['Meaning'])

        # Adding M2M table for field cf_entries on 'Meaning'
        m2m_table_name = db.shorten_name(u'dictionary_meaning_cf_entries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meaning', models.ForeignKey(orm[u'dictionary.meaning'], null=False)),
            ('entry', models.ForeignKey(orm[u'dictionary.entry'], null=False))
        ))
        db.create_unique(m2m_table_name, ['meaning_id', 'entry_id'])

        # Adding M2M table for field cf_collogroups on 'Meaning'
        m2m_table_name = db.shorten_name(u'dictionary_meaning_cf_collogroups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meaning', models.ForeignKey(orm[u'dictionary.meaning'], null=False)),
            ('collocationgroup', models.ForeignKey(orm[u'dictionary.collocationgroup'], null=False))
        ))
        db.create_unique(m2m_table_name, ['meaning_id', 'collocationgroup_id'])

        # Adding M2M table for field cf_meanings on 'Meaning'
        m2m_table_name = db.shorten_name(u'dictionary_meaning_cf_meanings')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_meaning', models.ForeignKey(orm[u'dictionary.meaning'], null=False)),
            ('to_meaning', models.ForeignKey(orm[u'dictionary.meaning'], null=False))
        ))
        db.create_unique(m2m_table_name, ['from_meaning_id', 'to_meaning_id'])

        # Adding model 'Example'
        db.create_table(u'dictionary_example', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meaning', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Meaning'], null=True, blank=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Entry'], null=True, blank=True)),
            ('collogroup', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.CollocationGroup'], null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=345, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('example', self.gf('django.db.models.fields.TextField')()),
            ('context', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('address_text', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('audited', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('greek_eq_status', self.gf('django.db.models.fields.CharField')(default=u'L', max_length=1)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['Example'])

        # Adding model 'CollocationGroup'
        db.create_table(u'dictionary_collocationgroup', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='collocationgroup_set', null=True, to=orm['dictionary.Entry'])),
            ('base_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='collocationgroup_set', null=True, to=orm['dictionary.Meaning'])),
            ('link_to_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_collogroup_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_collogroup_set', null=True, to=orm['dictionary.Meaning'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['CollocationGroup'])

        # Adding M2M table for field cf_entries on 'CollocationGroup'
        m2m_table_name = db.shorten_name(u'dictionary_collocationgroup_cf_entries')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('collocationgroup', models.ForeignKey(orm[u'dictionary.collocationgroup'], null=False)),
            ('entry', models.ForeignKey(orm[u'dictionary.entry'], null=False))
        ))
        db.create_unique(m2m_table_name, ['collocationgroup_id', 'entry_id'])

        # Adding M2M table for field cf_meanings on 'CollocationGroup'
        m2m_table_name = db.shorten_name(u'dictionary_collocationgroup_cf_meanings')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('collocationgroup', models.ForeignKey(orm[u'dictionary.collocationgroup'], null=False)),
            ('meaning', models.ForeignKey(orm[u'dictionary.meaning'], null=False))
        ))
        db.create_unique(m2m_table_name, ['collocationgroup_id', 'meaning_id'])

        # Adding model 'Collocation'
        db.create_table(u'dictionary_collocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collogroup', self.gf('django.db.models.fields.related.ForeignKey')(related_name='collocation_set', to=orm['dictionary.CollocationGroup'])),
            ('collocation', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('civil_equivalent', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['Collocation'])

        # Adding model 'GreekEquivalentForExample'
        db.create_table(u'dictionary_greekequivalentforexample', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('for_example', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Example'])),
            ('unitext', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('mark', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('initial_form', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('corrupted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['GreekEquivalentForExample'])

        # Adding model 'OrthographicVariant'
        db.create_table(u'dictionary_orthographicvariant', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='orthographic_variants', null=True, to=orm['dictionary.Entry'])),
            ('idem', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('no_ref_entry', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['OrthographicVariant'])

        # Adding model 'Participle'
        db.create_table(u'dictionary_participle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Entry'], null=True, blank=True)),
            ('tp', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('idem', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(default=0, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'dictionary', ['Participle'])


    def backwards(self, orm):
        # Deleting model 'Entry'
        db.delete_table(u'dictionary_entry')

        # Removing M2M table for field cf_entries on 'Entry'
        db.delete_table(db.shorten_name(u'dictionary_entry_cf_entries'))

        # Removing M2M table for field cf_collogroups on 'Entry'
        db.delete_table(db.shorten_name(u'dictionary_entry_cf_collogroups'))

        # Removing M2M table for field cf_meanings on 'Entry'
        db.delete_table(db.shorten_name(u'dictionary_entry_cf_meanings'))

        # Removing M2M table for field authors on 'Entry'
        db.delete_table(db.shorten_name(u'dictionary_entry_authors'))

        # Deleting model 'Etymology'
        db.delete_table(u'dictionary_etymology')

        # Deleting model 'MeaningContext'
        db.delete_table(u'dictionary_meaningcontext')

        # Deleting model 'Meaning'
        db.delete_table(u'dictionary_meaning')

        # Removing M2M table for field cf_entries on 'Meaning'
        db.delete_table(db.shorten_name(u'dictionary_meaning_cf_entries'))

        # Removing M2M table for field cf_collogroups on 'Meaning'
        db.delete_table(db.shorten_name(u'dictionary_meaning_cf_collogroups'))

        # Removing M2M table for field cf_meanings on 'Meaning'
        db.delete_table(db.shorten_name(u'dictionary_meaning_cf_meanings'))

        # Deleting model 'Example'
        db.delete_table(u'dictionary_example')

        # Deleting model 'CollocationGroup'
        db.delete_table(u'dictionary_collocationgroup')

        # Removing M2M table for field cf_entries on 'CollocationGroup'
        db.delete_table(db.shorten_name(u'dictionary_collocationgroup_cf_entries'))

        # Removing M2M table for field cf_meanings on 'CollocationGroup'
        db.delete_table(db.shorten_name(u'dictionary_collocationgroup_cf_meanings'))

        # Deleting model 'Collocation'
        db.delete_table(u'dictionary_collocation')

        # Deleting model 'GreekEquivalentForExample'
        db.delete_table(u'dictionary_greekequivalentforexample')

        # Deleting model 'OrthographicVariant'
        db.delete_table(u'dictionary_orthographicvariant')

        # Deleting model 'Participle'
        db.delete_table(u'dictionary_participle')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'custom_user.customuser': {
            'Meta': {'ordering': "('last_name', 'first_name')", 'object_name': 'CustomUser', '_ormbases': [u'auth.User']},
            'second_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            u'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'dictionary.collocation': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Collocation'},
            'civil_equivalent': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'collocation': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'collogroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'collocation_set'", 'to': u"orm['dictionary.CollocationGroup']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'dictionary.collocationgroup': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'CollocationGroup'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'base_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collocationgroup_set'", 'null': 'True', 'to': u"orm['dictionary.Entry']"}),
            'base_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collocationgroup_set'", 'null': 'True', 'to': u"orm['dictionary.Meaning']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_collogroup_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_collogroup_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.Meaning']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_collogroup_set'", 'null': 'True', 'to': u"orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_collogroup_set'", 'null': 'True', 'to': u"orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'dictionary.entry': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Entry'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'antconc_query': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['custom_user.CustomUser']", 'null': 'True', 'blank': 'True'}),
            'canonical_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cf_collogroups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.CollocationGroup']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.Meaning']"}),
            'civil_equivalent': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'derivation_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'derived_entry_set'", 'null': 'True', 'to': u"orm['dictionary.Entry']"}),
            'duplicate': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1', 'blank': 'True'}),
            'genitive': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'good': ('django.db.models.fields.TextField', [], {'default': "u'b'", 'max_length': '1'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'homonym_gloss': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'homonym_order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_collogroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_entry_set'", 'null': 'True', 'to': u"orm['dictionary.CollocationGroup']"}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_entry_set'", 'null': 'True', 'to': u"orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_entry_set'", 'null': 'True', 'to': u"orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {}),
            'nom_sg': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '25', 'blank': 'True'}),
            'onym': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1', 'blank': 'True'}),
            'part_of_speech': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1'}),
            'participle_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1', 'blank': 'True'}),
            'percent_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'possessive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'questionable_headword': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'reconstructed_headword': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sg1': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'sg2': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'short_form': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'c'", 'max_length': '1'}),
            'tantum': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1', 'blank': 'True'}),
            'transitivity': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1', 'blank': 'True'}),
            'uninflected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'word_forms_list': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'dictionary.etymology': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Etymology'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'collocation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.Collocation']", 'null': 'True', 'blank': 'True'}),
            'corrupted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.Entry']", 'null': 'True', 'blank': 'True'}),
            'etymon_to': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'etymon_set'", 'null': 'True', 'to': u"orm['dictionary.Etymology']"}),
            'gloss': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1'}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'meaning': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'questionable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'translit': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'unclear': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unitext': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'})
        },
        u'dictionary.example': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Example'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'address_text': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'audited': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'collogroup': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.CollocationGroup']", 'null': 'True', 'blank': 'True'}),
            'context': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.Entry']", 'null': 'True', 'blank': 'True'}),
            'example': ('django.db.models.fields.TextField', [], {}),
            'greek_eq_status': ('django.db.models.fields.CharField', [], {'default': "u'L'", 'max_length': '1'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meaning': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.Meaning']", 'null': 'True', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '345', 'blank': 'True'})
        },
        u'dictionary.greekequivalentforexample': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'GreekEquivalentForExample'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'corrupted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'for_example': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.Example']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_form': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            'unitext': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'dictionary.meaning': {
            'Meta': {'ordering': "('id',)", 'object_name': 'Meaning'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cf_collogroups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_meaning_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.CollocationGroup']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_meaning_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_meaning_set'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['dictionary.Meaning']"}),
            'collogroup_container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meaning_set'", 'null': 'True', 'to': u"orm['dictionary.CollocationGroup']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meaning_set'", 'null': 'True', 'to': u"orm['dictionary.Entry']"}),
            'gloss': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_collogroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': u"orm['dictionary.CollocationGroup']"}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': u"orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': u"orm['dictionary.Meaning']"}),
            'meaning': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'metaphorical': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '345', 'blank': 'True'}),
            'parent_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_meaning_set'", 'null': 'True', 'to': u"orm['dictionary.Meaning']"}),
            'substantivus': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'substantivus_type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '1', 'blank': 'True'})
        },
        u'dictionary.meaningcontext': {
            'Meta': {'object_name': 'MeaningContext'},
            'context': ('django.db.models.fields.CharField', [], {'max_length': '40', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'left_text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'meaning': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'right_text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'dictionary.orthographicvariant': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'OrthographicVariant'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'orthographic_variants'", 'null': 'True', 'to': u"orm['dictionary.Entry']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idem': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'no_ref_entry': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'dictionary.participle': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'Participle'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dictionary.Entry']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idem': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'default': '0', 'blank': 'True'}),
            'tp': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['dictionary']