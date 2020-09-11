# Generated by Django 2.2.13 on 2020-09-09 09:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('custom_user', '0002_auto_20180307_1354'),
        ('dictionary', '0064_auto_20200720_1501'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='temp_deadline',
            field=models.DateTimeField(blank=True, null=True, verbose_name='дедлайн для временных редакторов'),
        ),
        migrations.AddField(
            model_name='entry',
            name='temp_editors',
            field=models.ManyToManyField(blank=True, related_name='temp_editors_set', to='custom_user.CustomUser', verbose_name='временные редакторы'),
        ),
        migrations.AlterField(
            model_name='tip',
            name='ref',
            field=models.CharField(choices=[('Collocation.civil_equivalent', 'Collocation.civil_equivalent'), ('Collocation.collocation', 'Collocation.collocation'), ('CollocationGroup.additional_info', 'CollocationGroup.additional_info'), ('CollocationGroup.hidden', 'CollocationGroup.hidden'), ('CollocationGroup.phraseological', 'CollocationGroup.phraseological'), ('Entry.additional_info', 'Entry.additional_info'), ('Entry.antconc_query', 'Entry.antconc_query'), ('Entry.canonical_name', 'Entry.canonical_name'), ('Entry.civil_equivalent', 'Entry.civil_equivalent'), ('Entry.comparative', 'Entry.comparative'), ('Entry.gender', 'Entry.gender'), ('Entry.genitive', 'Entry.genitive'), ('Entry.hidden', 'Entry.hidden'), ('Entry.homonym_gloss', 'Entry.homonym_gloss'), ('Entry.homonym_order', 'Entry.homonym_order'), ('Entry.nom_sg', 'Entry.nom_sg'), ('Entry.onym', 'Entry.onym'), ('Entry.part_of_speech', 'Entry.part_of_speech'), ('Entry.participle_type', 'Entry.participle_type'), ('Entry.possessive', 'Entry.possessive'), ('Entry.sg1', 'Entry.sg1'), ('Entry.sg2', 'Entry.sg2'), ('Entry.short_form', 'Entry.short_form'), ('Entry.special_case', 'Entry.special_case'), ('Entry.tantum', 'Entry.tantum'), ('Entry.temp_deadline', 'Entry.temp_deadline'), ('Entry.template_version', 'Entry.template_version'), ('Entry.transitivity', 'Entry.transitivity'), ('Entry.uninflected', 'Entry.uninflected'), ('Etymology.additional_info', 'Etymology.additional_info'), ('Etymology.gloss', 'Etymology.gloss'), ('Etymology.language', 'Etymology.language'), ('Etymology.mark', 'Etymology.mark'), ('Etymology.meaning', 'Etymology.meaning'), ('Etymology.questionable', 'Etymology.questionable'), ('Etymology.source', 'Etymology.source'), ('Etymology.text', 'Etymology.text'), ('Etymology.translit', 'Etymology.translit'), ('Etymology.unclear', 'Etymology.unclear'), ('Etymology.unitext', 'Etymology.unitext'), ('Example.additional_info', 'Example.additional_info'), ('Example.address_text', 'Example.address_text'), ('Example.context', 'Example.context'), ('Example.example', 'Example.example'), ('Example.greek_eq_status', 'Example.greek_eq_status'), ('Example.note', 'Example.note'), ('Example.wordform_example', 'Example.wordform_example'), ('GreekEquivalentForExample.additional_info', 'GreekEquivalentForExample.additional_info'), ('GreekEquivalentForExample.aliud', 'GreekEquivalentForExample.aliud'), ('GreekEquivalentForExample.initial_form', 'GreekEquivalentForExample.initial_form'), ('GreekEquivalentForExample.initial_form_phraseology', 'GreekEquivalentForExample.initial_form_phraseology'), ('GreekEquivalentForExample.mark', 'GreekEquivalentForExample.mark'), ('GreekEquivalentForExample.note', 'GreekEquivalentForExample.note'), ('GreekEquivalentForExample.order', 'GreekEquivalentForExample.order'), ('GreekEquivalentForExample.position', 'GreekEquivalentForExample.position'), ('GreekEquivalentForExample.source', 'GreekEquivalentForExample.source'), ('GreekEquivalentForExample.unitext', 'GreekEquivalentForExample.unitext'), ('Meaning.additional_info', 'Meaning.additional_info'), ('Meaning.figurative', 'Meaning.figurative'), ('Meaning.gloss', 'Meaning.gloss'), ('Meaning.hidden', 'Meaning.hidden'), ('Meaning.is_valency', 'Meaning.is_valency'), ('Meaning.meaning', 'Meaning.meaning'), ('Meaning.metaphorical', 'Meaning.metaphorical'), ('Meaning.numex', 'Meaning.numex'), ('Meaning.special_case', 'Meaning.special_case'), ('Meaning.substantivus', 'Meaning.substantivus'), ('Meaning.substantivus_csl', 'Meaning.substantivus_csl'), ('Meaning.substantivus_type', 'Meaning.substantivus_type'), ('Meaning.transitivity', 'Meaning.transitivity'), ('MeaningContext.context', 'MeaningContext.context'), ('MeaningContext.left_text', 'MeaningContext.left_text'), ('MeaningContext.right_text', 'MeaningContext.right_text'), ('OrthographicVariant.idem', 'OrthographicVariant.idem'), ('OrthographicVariant.no_ref_entry', 'OrthographicVariant.no_ref_entry'), ('OrthographicVariant.order', 'OrthographicVariant.order'), ('OrthographicVariant.questionable', 'OrthographicVariant.questionable'), ('OrthographicVariant.reconstructed', 'OrthographicVariant.reconstructed'), ('OrthographicVariant.untitled_exists', 'OrthographicVariant.untitled_exists'), ('OrthographicVariant.use', 'OrthographicVariant.use'), ('OrthographicVariant.without_accent', 'OrthographicVariant.without_accent'), ('Participle.idem', 'Participle.idem'), ('Participle.order', 'Participle.order'), ('Participle.tp', 'Participle.tp'), ('Translation.additional_info', 'Translation.additional_info'), ('Translation.fragment_end', 'Translation.fragment_end'), ('Translation.fragment_start', 'Translation.fragment_start'), ('Translation.fragmented', 'Translation.fragmented'), ('Translation.hidden', 'Translation.hidden'), ('Translation.order', 'Translation.order'), ('Translation.source', 'Translation.source'), ('Translation.translation', 'Translation.translation')], max_length=50, primary_key=True, serialize=False, verbose_name='поле, к которому относится подсказка'),
        ),
    ]