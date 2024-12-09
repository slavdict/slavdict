# Generated by Django 2.2.28 on 2024-07-28 22:00

from django.db import migrations, models
import slavdict.dictionary.models


class Migration(migrations.Migration):

    dependencies = [
        ('dictionary', '0089_auto_20231015_0157'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranslationSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Источник перевода')),
                ('label', models.CharField(max_length=100, verbose_name='Обозначение в словаре')),
            ],
            options={
                'verbose_name': 'источник перевода',
                'verbose_name_plural': 'ИСТОЧНИКИ ПЕРЕВОДА',
                'ordering': ('id',),
            },
            bases=(models.Model, slavdict.dictionary.models.JSONSerializable, slavdict.dictionary.models.VolumeAttributive),
        ),
        migrations.AlterField(
            model_name='collocation',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='collocationgroup',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='entry',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], default=0, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='etymology',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='example',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='greekequivalentforexample',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='meaning',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='meaningcontext',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='orthographicvariant',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='participle',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
        migrations.AlterField(
            model_name='tip',
            name='ref',
            field=models.CharField(choices=[('Collocation.civil_equivalent', 'Collocation.civil_equivalent'), ('Collocation.collocation', 'Collocation.collocation'), ('Collocation.volume', 'Collocation.volume'), ('CollocationGroup.additional_info', 'CollocationGroup.additional_info'), ('CollocationGroup.hidden', 'CollocationGroup.hidden'), ('CollocationGroup.phraseological', 'CollocationGroup.phraseological'), ('CollocationGroup.volume', 'CollocationGroup.volume'), ('Entry.HEADWORD', 'Entry.HEADWORD'), ('Entry.additional_info', 'Entry.additional_info'), ('Entry.antconc_query', 'Entry.antconc_query'), ('Entry.canonical_name', 'Entry.canonical_name'), ('Entry.civil_equivalent', 'Entry.civil_equivalent'), ('Entry.comparative', 'Entry.comparative'), ('Entry.gender', 'Entry.gender'), ('Entry.genitive', 'Entry.genitive'), ('Entry.hidden', 'Entry.hidden'), ('Entry.homonym_gloss', 'Entry.homonym_gloss'), ('Entry.homonym_order', 'Entry.homonym_order'), ('Entry.inverted_sort_key1', 'Entry.inverted_sort_key1'), ('Entry.inverted_sort_key2', 'Entry.inverted_sort_key2'), ('Entry.nom_pl', 'Entry.nom_pl'), ('Entry.onym', 'Entry.onym'), ('Entry.part_of_speech', 'Entry.part_of_speech'), ('Entry.participle_type', 'Entry.participle_type'), ('Entry.possessive', 'Entry.possessive'), ('Entry.restricted_use', 'Entry.restricted_use'), ('Entry.sg1', 'Entry.sg1'), ('Entry.sg2', 'Entry.sg2'), ('Entry.short_form', 'Entry.short_form'), ('Entry.sort_key1', 'Entry.sort_key1'), ('Entry.sort_key2', 'Entry.sort_key2'), ('Entry.special_case', 'Entry.special_case'), ('Entry.tantum', 'Entry.tantum'), ('Entry.template_version', 'Entry.template_version'), ('Entry.tmp_volume', 'Entry.tmp_volume'), ('Entry.transitivity', 'Entry.transitivity'), ('Entry.uninflected', 'Entry.uninflected'), ('Entry.volume', 'Entry.volume'), ('Etymology.additional_info', 'Etymology.additional_info'), ('Etymology.gloss', 'Etymology.gloss'), ('Etymology.language', 'Etymology.language'), ('Etymology.mark', 'Etymology.mark'), ('Etymology.meaning', 'Etymology.meaning'), ('Etymology.questionable', 'Etymology.questionable'), ('Etymology.source', 'Etymology.source'), ('Etymology.text', 'Etymology.text'), ('Etymology.translit', 'Etymology.translit'), ('Etymology.unclear', 'Etymology.unclear'), ('Etymology.unitext', 'Etymology.unitext'), ('Etymology.volume', 'Etymology.volume'), ('Example.additional_info', 'Example.additional_info'), ('Example.address_text', 'Example.address_text'), ('Example.context', 'Example.context'), ('Example.dont_lowercase', 'Example.dont_lowercase'), ('Example.example', 'Example.example'), ('Example.greek_eq_status', 'Example.greek_eq_status'), ('Example.note', 'Example.note'), ('Example.volume', 'Example.volume'), ('Example.wordform_example', 'Example.wordform_example'), ('GreekEquivalentForExample.additional_info', 'GreekEquivalentForExample.additional_info'), ('GreekEquivalentForExample.aliud', 'GreekEquivalentForExample.aliud'), ('GreekEquivalentForExample.initial_form', 'GreekEquivalentForExample.initial_form'), ('GreekEquivalentForExample.initial_form_phraseology', 'GreekEquivalentForExample.initial_form_phraseology'), ('GreekEquivalentForExample.mark', 'GreekEquivalentForExample.mark'), ('GreekEquivalentForExample.note', 'GreekEquivalentForExample.note'), ('GreekEquivalentForExample.order', 'GreekEquivalentForExample.order'), ('GreekEquivalentForExample.position', 'GreekEquivalentForExample.position'), ('GreekEquivalentForExample.source', 'GreekEquivalentForExample.source'), ('GreekEquivalentForExample.unitext', 'GreekEquivalentForExample.unitext'), ('GreekEquivalentForExample.volume', 'GreekEquivalentForExample.volume'), ('Meaning.additional_info', 'Meaning.additional_info'), ('Meaning.figurative', 'Meaning.figurative'), ('Meaning.gloss', 'Meaning.gloss'), ('Meaning.hidden', 'Meaning.hidden'), ('Meaning.is_valency', 'Meaning.is_valency'), ('Meaning.meaning', 'Meaning.meaning'), ('Meaning.metaphorical', 'Meaning.metaphorical'), ('Meaning.numex', 'Meaning.numex'), ('Meaning.special_case', 'Meaning.special_case'), ('Meaning.substantivus', 'Meaning.substantivus'), ('Meaning.substantivus_csl', 'Meaning.substantivus_csl'), ('Meaning.substantivus_type', 'Meaning.substantivus_type'), ('Meaning.transitivity', 'Meaning.transitivity'), ('Meaning.volume', 'Meaning.volume'), ('MeaningContext.context', 'MeaningContext.context'), ('MeaningContext.left_text', 'MeaningContext.left_text'), ('MeaningContext.right_text', 'MeaningContext.right_text'), ('MeaningContext.volume', 'MeaningContext.volume'), ('OrthographicVariant.idem', 'OrthographicVariant.idem'), ('OrthographicVariant.no_ref_entry', 'OrthographicVariant.no_ref_entry'), ('OrthographicVariant.order', 'OrthographicVariant.order'), ('OrthographicVariant.questionable', 'OrthographicVariant.questionable'), ('OrthographicVariant.reconstructed', 'OrthographicVariant.reconstructed'), ('OrthographicVariant.untitled_exists', 'OrthographicVariant.untitled_exists'), ('OrthographicVariant.use', 'OrthographicVariant.use'), ('OrthographicVariant.volume', 'OrthographicVariant.volume'), ('OrthographicVariant.without_accent', 'OrthographicVariant.without_accent'), ('Participle.idem', 'Participle.idem'), ('Participle.order', 'Participle.order'), ('Participle.tp', 'Participle.tp'), ('Participle.volume', 'Participle.volume'), ('Translation.additional_info', 'Translation.additional_info'), ('Translation.fragment_end', 'Translation.fragment_end'), ('Translation.fragment_start', 'Translation.fragment_start'), ('Translation.fragmented', 'Translation.fragmented'), ('Translation.hidden', 'Translation.hidden'), ('Translation.order', 'Translation.order'), ('Translation.source', 'Translation.source'), ('Translation.translation', 'Translation.translation'), ('Translation.volume', 'Translation.volume'), ('TranslationSource.label', 'TranslationSource.label'), ('TranslationSource.name', 'TranslationSource.name')], max_length=50, primary_key=True, serialize=False, verbose_name='поле, к которому относится подсказка'),
        ),
        migrations.AlterField(
            model_name='translation',
            name='volume',
            field=models.SmallIntegerField(blank=True, choices=[(0, 'Вне томов'), (1, 'Том I (А, Б)'), (2, 'Том II (В)'), (3, 'Том III (Г, Д, Е)'), (4, 'Том IV (Ж, З)'), (5, 'Том V (И)'), (6, 'Том VI (К)'), (7, 'Том VII (Л, М)'), (8, 'Том VIII (Н)'), (9, 'Том IX (О)'), (10, 'Том X (П)'), (11, 'Том XI (Р, С)'), (12, 'Том XII (Т, У, Ф, Х, Ц, Ч, Ш, Щ, Ю, Я)')], null=True, verbose_name='том'),
        ),
    ]