# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Entry'
        db.create_table('dictionary_entry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('civil_equivalent', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('homonym_order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('homonym_gloss', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('part_of_speech', self.gf('django.db.models.fields.related.ForeignKey')(related_name='entries_of_pos', null=True, to=orm['directory.CategoryValue'])),
            ('uninflected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('word_forms_list', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('tantum', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entries_of_tantum', null=True, to=orm['directory.CategoryValue'])),
            ('gender', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entries_of_gender', null=True, to=orm['directory.CategoryValue'])),
            ('genitive', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('onym', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.CategoryValue'], null=True, blank=True)),
            ('canonical_name', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('nom_sg', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('nom_pl', self.gf('django.db.models.fields.CharField')(max_length=25, null=True, blank=True)),
            ('short_form', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('possessive', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('transitivity', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entries_of_transitivity', null=True, to=orm['directory.CategoryValue'])),
            ('sg1', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('sg2', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('participle_type', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entries_of_parttype', null=True, to=orm['directory.CategoryValue'])),
            ('derivation_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='derived_entry_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_entry_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_collogroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_entry_set', null=True, to=orm['dictionary.CollocationGroup'])),
            ('link_to_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_entry_set', null=True, to=orm['dictionary.Meaning'])),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='entries_of_status', null=True, to=orm['directory.CategoryValue'])),
            ('percent_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('editor', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['custom_user.CustomUser'], null=True, blank=True)),
            ('antconc_query', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('grequiv_status', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')()),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['Entry'])

        # Adding M2M table for field cf_entries on 'Entry'
        db.create_table('dictionary_entry_cf_entries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_entry', models.ForeignKey(orm['dictionary.entry'], null=False)),
            ('to_entry', models.ForeignKey(orm['dictionary.entry'], null=False))
        ))
        db.create_unique('dictionary_entry_cf_entries', ['from_entry_id', 'to_entry_id'])

        # Adding M2M table for field cf_collogroups on 'Entry'
        db.create_table('dictionary_entry_cf_collogroups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['dictionary.entry'], null=False)),
            ('collocationgroup', models.ForeignKey(orm['dictionary.collocationgroup'], null=False))
        ))
        db.create_unique('dictionary_entry_cf_collogroups', ['entry_id', 'collocationgroup_id'])

        # Adding M2M table for field cf_meanings on 'Entry'
        db.create_table('dictionary_entry_cf_meanings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('entry', models.ForeignKey(orm['dictionary.entry'], null=False)),
            ('meaning', models.ForeignKey(orm['dictionary.meaning'], null=False))
        ))
        db.create_unique('dictionary_entry_cf_meanings', ['entry_id', 'meaning_id'])

        # Adding model 'Etymology'
        db.create_table('dictionary_etymology', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Entry'], null=True, blank=True)),
            ('collocation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Collocation'], null=True, blank=True)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('etymon_to', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='etymon_set', null=True, to=orm['dictionary.Etymology'])),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.CategoryValue'])),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('translit', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('meaning', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('gloss', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('unclear', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('questionable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('mark', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['Etymology'])

        # Adding model 'MeaningContext'
        db.create_table('dictionary_meaningcontext', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meaning', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Meaning'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('left_text', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('context', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('right_text', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['MeaningContext'])

        # Adding model 'Meaning'
        db.create_table('dictionary_meaning', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry_container', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='meaning_set', null=True, to=orm['dictionary.Entry'])),
            ('collogroup_container', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='meaning_set', null=True, to=orm['dictionary.CollocationGroup'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('parent_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='child_meaning_set', null=True, to=orm['dictionary.Meaning'])),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('link_to_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_meaning_set', null=True, to=orm['dictionary.Meaning'])),
            ('link_to_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_meaning_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_collogroup', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_meaning_set', null=True, to=orm['dictionary.CollocationGroup'])),
            ('metaphorical', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('meaning', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('gloss', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('substantivus', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('substantivus_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['directory.CategoryValue'], null=True, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['Meaning'])

        # Adding M2M table for field cf_entries on 'Meaning'
        db.create_table('dictionary_meaning_cf_entries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meaning', models.ForeignKey(orm['dictionary.meaning'], null=False)),
            ('entry', models.ForeignKey(orm['dictionary.entry'], null=False))
        ))
        db.create_unique('dictionary_meaning_cf_entries', ['meaning_id', 'entry_id'])

        # Adding M2M table for field cf_collogroups on 'Meaning'
        db.create_table('dictionary_meaning_cf_collogroups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('meaning', models.ForeignKey(orm['dictionary.meaning'], null=False)),
            ('collocationgroup', models.ForeignKey(orm['dictionary.collocationgroup'], null=False))
        ))
        db.create_unique('dictionary_meaning_cf_collogroups', ['meaning_id', 'collocationgroup_id'])

        # Adding M2M table for field cf_meanings on 'Meaning'
        db.create_table('dictionary_meaning_cf_meanings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_meaning', models.ForeignKey(orm['dictionary.meaning'], null=False)),
            ('to_meaning', models.ForeignKey(orm['dictionary.meaning'], null=False))
        ))
        db.create_unique('dictionary_meaning_cf_meanings', ['from_meaning_id', 'to_meaning_id'])

        # Adding model 'Example'
        db.create_table('dictionary_example', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('meaning', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Meaning'])),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('example', self.gf('django.db.models.fields.TextField')()),
            ('context', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('address_text', self.gf('django.db.models.fields.CharField')(max_length=300, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('greek_eq_status', self.gf('django.db.models.fields.CharField')(default=u'L', max_length=1)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['Example'])

        # Adding model 'CollocationGroup'
        db.create_table('dictionary_collocationgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='collocationgroup_set', null=True, to=orm['dictionary.Entry'])),
            ('base_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='collocationgroup_set', null=True, to=orm['dictionary.Meaning'])),
            ('link_to_entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_collogroup_set', null=True, to=orm['dictionary.Entry'])),
            ('link_to_meaning', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='ref_collogroup_set', null=True, to=orm['dictionary.Meaning'])),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['CollocationGroup'])

        # Adding M2M table for field cf_entries on 'CollocationGroup'
        db.create_table('dictionary_collocationgroup_cf_entries', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('collocationgroup', models.ForeignKey(orm['dictionary.collocationgroup'], null=False)),
            ('entry', models.ForeignKey(orm['dictionary.entry'], null=False))
        ))
        db.create_unique('dictionary_collocationgroup_cf_entries', ['collocationgroup_id', 'entry_id'])

        # Adding M2M table for field cf_meanings on 'CollocationGroup'
        db.create_table('dictionary_collocationgroup_cf_meanings', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('collocationgroup', models.ForeignKey(orm['dictionary.collocationgroup'], null=False)),
            ('meaning', models.ForeignKey(orm['dictionary.meaning'], null=False))
        ))
        db.create_unique('dictionary_collocationgroup_cf_meanings', ['collocationgroup_id', 'meaning_id'])

        # Adding model 'Collocation'
        db.create_table('dictionary_collocation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('collogroup', self.gf('django.db.models.fields.related.ForeignKey')(related_name='collocation_set', to=orm['dictionary.CollocationGroup'])),
            ('collocation', self.gf('django.db.models.fields.CharField')(max_length=70)),
            ('civil_equivalent', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['Collocation'])

        # Adding model 'GreekEquivalentForMeaning'
        db.create_table('dictionary_greekequivalentformeaning', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mark', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('for_meaning', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Meaning'])),
        ))
        db.send_create_signal('dictionary', ['GreekEquivalentForMeaning'])

        # Adding model 'GreekEquivalentForExample'
        db.create_table('dictionary_greekequivalentforexample', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('mark', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=40, blank=True)),
            ('additional_info', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('for_example', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Example'])),
            ('position', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['GreekEquivalentForExample'])

        # Adding model 'OrthographicVariant'
        db.create_table('dictionary_orthographicvariant', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='orthographic_variants', null=True, to=orm['dictionary.Entry'])),
            ('idem', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('is_reconstructed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_approved', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('frequency', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['OrthographicVariant'])

        # Adding model 'WordForm'
        db.create_table('dictionary_wordform', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('entry', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dictionary.Entry'], null=True, blank=True)),
            ('tp', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('idem', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('order', self.gf('django.db.models.fields.SmallIntegerField')(null=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['WordForm'])

        # Adding model 'SynonymGroup'
        db.create_table('dictionary_synonymgroup', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('base', self.gf('django.db.models.fields.related.ForeignKey')(related_name='base_synonym_in', to=orm['dictionary.Entry'])),
            ('ctime', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('mtime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('dictionary', ['SynonymGroup'])

        # Adding M2M table for field entry_synonyms on 'SynonymGroup'
        db.create_table('dictionary_synonymgroup_entry_synonyms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('synonymgroup', models.ForeignKey(orm['dictionary.synonymgroup'], null=False)),
            ('entry', models.ForeignKey(orm['dictionary.entry'], null=False))
        ))
        db.create_unique('dictionary_synonymgroup_entry_synonyms', ['synonymgroup_id', 'entry_id'])

        # Adding M2M table for field collogroup_synonyms on 'SynonymGroup'
        db.create_table('dictionary_synonymgroup_collogroup_synonyms', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('synonymgroup', models.ForeignKey(orm['dictionary.synonymgroup'], null=False)),
            ('collocationgroup', models.ForeignKey(orm['dictionary.collocationgroup'], null=False))
        ))
        db.create_unique('dictionary_synonymgroup_collogroup_synonyms', ['synonymgroup_id', 'collocationgroup_id'])


    def backwards(self, orm):
        
        # Deleting model 'Entry'
        db.delete_table('dictionary_entry')

        # Removing M2M table for field cf_entries on 'Entry'
        db.delete_table('dictionary_entry_cf_entries')

        # Removing M2M table for field cf_collogroups on 'Entry'
        db.delete_table('dictionary_entry_cf_collogroups')

        # Removing M2M table for field cf_meanings on 'Entry'
        db.delete_table('dictionary_entry_cf_meanings')

        # Deleting model 'Etymology'
        db.delete_table('dictionary_etymology')

        # Deleting model 'MeaningContext'
        db.delete_table('dictionary_meaningcontext')

        # Deleting model 'Meaning'
        db.delete_table('dictionary_meaning')

        # Removing M2M table for field cf_entries on 'Meaning'
        db.delete_table('dictionary_meaning_cf_entries')

        # Removing M2M table for field cf_collogroups on 'Meaning'
        db.delete_table('dictionary_meaning_cf_collogroups')

        # Removing M2M table for field cf_meanings on 'Meaning'
        db.delete_table('dictionary_meaning_cf_meanings')

        # Deleting model 'Example'
        db.delete_table('dictionary_example')

        # Deleting model 'CollocationGroup'
        db.delete_table('dictionary_collocationgroup')

        # Removing M2M table for field cf_entries on 'CollocationGroup'
        db.delete_table('dictionary_collocationgroup_cf_entries')

        # Removing M2M table for field cf_meanings on 'CollocationGroup'
        db.delete_table('dictionary_collocationgroup_cf_meanings')

        # Deleting model 'Collocation'
        db.delete_table('dictionary_collocation')

        # Deleting model 'GreekEquivalentForMeaning'
        db.delete_table('dictionary_greekequivalentformeaning')

        # Deleting model 'GreekEquivalentForExample'
        db.delete_table('dictionary_greekequivalentforexample')

        # Deleting model 'OrthographicVariant'
        db.delete_table('dictionary_orthographicvariant')

        # Deleting model 'WordForm'
        db.delete_table('dictionary_wordform')

        # Deleting model 'SynonymGroup'
        db.delete_table('dictionary_synonymgroup')

        # Removing M2M table for field entry_synonyms on 'SynonymGroup'
        db.delete_table('dictionary_synonymgroup_entry_synonyms')

        # Removing M2M table for field collogroup_synonyms on 'SynonymGroup'
        db.delete_table('dictionary_synonymgroup_collogroup_synonyms')


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
            'civil_equivalent': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'collocation': ('django.db.models.fields.CharField', [], {'max_length': '70'}),
            'collogroup': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'collocation_set'", 'to': "orm['dictionary.CollocationGroup']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dictionary.collocationgroup': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'CollocationGroup'},
            'base_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collocationgroup_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'base_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'collocationgroup_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_collogroup_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_collogroup_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Meaning']"}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_collogroup_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_collogroup_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dictionary.entry': {
            'Meta': {'ordering': "('-id',)", 'object_name': 'Entry'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'antconc_query': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'canonical_name': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'cf_collogroups': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.CollocationGroup']"}),
            'cf_entries': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Entry']"}),
            'cf_meanings': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'cf_entry_set'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Meaning']"}),
            'civil_equivalent': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
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
            'mtime': ('django.db.models.fields.DateTimeField', [], {}),
            'nom_pl': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'nom_sg': ('django.db.models.fields.CharField', [], {'max_length': '25', 'null': 'True', 'blank': 'True'}),
            'onym': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['directory.CategoryValue']", 'null': 'True', 'blank': 'True'}),
            'part_of_speech': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries_of_pos'", 'null': 'True', 'to': "orm['directory.CategoryValue']"}),
            'participle_type': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entries_of_parttype'", 'null': 'True', 'to': "orm['directory.CategoryValue']"}),
            'percent_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'possessive': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sg1': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'sg2': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'short_form': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
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
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dictionary.greekequivalentforexample': {
            'Meta': {'object_name': 'GreekEquivalentForExample'},
            'additional_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'for_example': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Example']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mark': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_container': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'meaning_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'gloss': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_to_collogroup': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': "orm['dictionary.CollocationGroup']"}),
            'link_to_entry': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': "orm['dictionary.Entry']"}),
            'link_to_meaning': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'ref_meaning_set'", 'null': 'True', 'to': "orm['dictionary.Meaning']"}),
            'meaning': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'metaphorical': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
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
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'dictionary.synonymgroup': {
            'Meta': {'object_name': 'SynonymGroup'},
            'base': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'base_synonym_in'", 'to': "orm['dictionary.Entry']"}),
            'collogroup_synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['dictionary.CollocationGroup']", 'null': 'True', 'blank': 'True'}),
            'ctime': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'entry_synonyms': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'synonym_in'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['dictionary.Entry']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'dictionary.wordform': {
            'Meta': {'ordering': "('order', 'id')", 'object_name': 'WordForm'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dictionary.Entry']", 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'idem': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'mtime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'order': ('django.db.models.fields.SmallIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tp': ('django.db.models.fields.CharField', [], {'max_length': '2'})
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
