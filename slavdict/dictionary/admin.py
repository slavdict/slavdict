# encoding: UTF-8
import copy

from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.utils.safestring import mark_safe

from slavdict.admin import ui
from slavdict.custom_user.models import CustomUser
from slavdict.dictionary.models import Collocation
from slavdict.dictionary.models import CollocationGroup
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import Etymology
from slavdict.dictionary.models import Example
from slavdict.dictionary.models import GreekEquivalentForExample
from slavdict.dictionary.models import Meaning
from slavdict.dictionary.models import MeaningContext
from slavdict.dictionary.models import OrthographicVariant
from slavdict.dictionary.models import Participle

admin.site.login_template = ui.login_template

def staff_has_permission(self, request, obj=None):
    if obj is None:
        pass
    elif isinstance(obj, Entry):
        if request.user.preplock and obj.first_volume:
            return False
    else:
        try:
            entry = obj.host_entry
        except:
            return False
        else:
            if request.user.preplock and entry.first_volume:
                return False
    return request.user.is_staff

def superuser_has_permission(self, request, obj=None):
    if obj is None:
        pass
    elif isinstance(obj, Entry):
        if request.user.preplock and obj.first_volume:
            return False
    else:
        try:
            entry = obj.host_entry
        except:
            return False
        else:
            if request.user.preplock and entry.first_volume:
                return False
    return request.user.is_superuser

def host_entry(self):
    try:
        entry = self.host_entry
    except:
        return u'не относится ни к какой статье'
    else:
        if entry:
            html = u'<a href="%s" target="_blank">%s</a>' % (
                        entry.get_absolute_url(),
                        entry.civil_equivalent)
            return mark_safe(html)
        else:
            return u'не относится ни к какой статье'

host_entry.short_description = u'словарная статья'

def host_collogroup(self):
    html = u''
    try:
        host = self.host
    except:
        return html
    else:
        if isinstance(host, CollocationGroup):
            html = u'<a href="%s">%s</a>' % (
                        '/admin/dictionary/collocationgroup/?id=%s' % host.id,
                        host)
            html = mark_safe(html)
        return html

host_collogroup.short_description = u'Словосочетание'

def parent_meaning(self):
    text = u''
    if self.parent_meaning:
        mid = self.parent_meaning.id
        text = u'<a href="%s" target="_blank">%s</a>' % (
                    '/admin/dictionary/meaning/?id=%s' % mid, mid)
    return mark_safe(text)

parent_meaning.admin_order_field = 'parent_meaning_id'

def _orth_vars(obj):
    orth_vars = [unicode(i) for i in obj.orthographic_variants.all().order_by('id')]
    delimiter = u', '
    return delimiter.join(orth_vars)

def _collocations(obj):
    collocations = [unicode(i) for i in obj.collocation_set.all().order_by('id')]
    delimiter = u', '
    return delimiter.join(collocations)

def entry_with_orth_variants(obj):
    if obj.homonym_order:
        h = u' %s' % unicode(obj.homonym_order)
    else:
        h = u''
    x = _orth_vars(obj)
    e = obj.civil_equivalent
    if e:
        result = u'%s%s (%s%s)' % (x, h, e, h)
    else:
        result = u'%s%s' % (x, h)
    return result

entry_with_orth_variants.admin_order_field = 'civil_equivalent'
entry_with_orth_variants.short_description = u'словарная статья'

def meaning_with_entry(obj):
    econtainer = obj.entry_container
    if econtainer:
        ent = entry_with_orth_variants(econtainer)
    else:
        cgcontainer = obj.collogroup_container
        if cgcontainer:
            ent = _collocations(cgcontainer)
        else:
            ent = u'(БЕСХОЗНОЕ ЗНАЧЕНИЕ)'
    return u'%s [%s] %s' % (ent, obj.id, obj.meaning)

meaning_with_entry.admin_order_field = 'entry_container'
meaning_with_entry.short_description = u'значение'

def example_with_entry(obj):
    return u'%s [%s] %s' % (meaning_with_entry(obj.meaning), obj.id, obj.example)

def meaning_for_example(obj):
    m = obj.meaning
    if m is None:
        return u'<None>'
    return u'%s [%s]%s' % (m.meaning, m.id, u'*' if m.metaphorical else u'')

def entry_for_example(obj):
    m = obj.meaning
    e = m and m.entry_container
    if e:
        r = entry_with_orth_variants(e)
        i = u' [%s]' % e.id
    else:
        cg = m and m.collogroup_container
        if cg:
            r = _collocations(cg)
        else:
            r = u'(БЕСХОЗНОЕ ЗНАЧЕНИЕ)'
        i = u''
    return u'%s%s' % (r, i)


class FirstVolumeFilter(admin.SimpleListFilter):
    title = u'1-й том'
    parameter_name = 'first_volume'
    def lookups(self, request, model_admin):
        return (
            ('1', u'из 1-го тома'),
            ('0', u'остальные'),
        )
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(id__in=self.xs())
        if self.value() == '0':
            return queryset.filter(~Q(id__in=self.xs()))

class FirstVolumeEntryFilter(FirstVolumeFilter):
    def xs(self):
        return (e.id for e in Entry.objects.all() if e.first_volume)

class FirstVolumeCollogroupFilter(FirstVolumeFilter):
    def xs(self):
        return (x.id for x in CollocationGroup.objects.all() if x.first_volume)

class FirstVolumeMeaningFilter(FirstVolumeFilter):
    def xs(self):
        return (m.id for m in Meaning.objects.all() if m.not_hidden() and m.first_volume)

class FirstVolumeExampleFilter(FirstVolumeFilter):
    def xs(self):
        return (x.id for x in Example.objects.all() if x.first_volume)

class SubstantivusMeaningFilter(admin.SimpleListFilter):
    title = u'в роли сущ.'
    parameter_name = 'substantivus'
    def lookups(self, request, model_admin):
        return (
            ('1', u'в роли сущ.'),
            ('0', u'остальные'),
        )
    def xs(self):
        pattern = u'в роли сущ.'
        return (x.id for x in Meaning.objects.filter(
                    Q(gloss__icontains=pattern)|
                    Q(meaning__icontains=pattern)))
    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(Q(substantivus=True)|Q(id__in=self.xs()))
        if self.value() == '0':
            return queryset.exclude(Q(substantivus=True)|Q(id__in=self.xs()))



class OrthVar_Inline(admin.StackedInline):
    model = OrthographicVariant
    extra = 0
    fieldsets = (
        (None, {
            'fields': (('idem', 'no_ref_entry'),),
            }),
        )




ETYMOLOGY_FIELDSETS = (
    (u'Является этимоном для др. этимона',
        {'fields': ('etymon_to', 'questionable'),
        'classes': ('collapse',)}
        ),
    (None,
        {'fields': (
            'language',
            ('text', 'unitext', 'corrupted'),
            'translit',
            'meaning',
            'gloss',
            'unclear',
            'mark',
            'source')}
        ),
    (u'Примечание к этимологии',
        {'fields': ('additional_info',),
        'classes': ('collapse',)}
        ),
    )
class Etymology_Inline(admin.StackedInline):
    model = Etymology
    extra = 0
    fieldsets = ETYMOLOGY_FIELDSETS




class EtymologyForCollocation_Inline(admin.StackedInline):
    model = Etymology
    extra = 1
    fieldsets = ETYMOLOGY_FIELDSETS




class GreekEquivalentForExample_Inline(admin.StackedInline):
    model = GreekEquivalentForExample
    extra = 0
    fieldsets = (
        (None, {
            'fields': (
                ('unitext', 'corrupted'),
                'mark',
                'source',
                'initial_form',
                'order',
                ),
            }),
        (u'Примечание к параллели',
            {'fields': ('additional_info', 'note'),
            'classes': ('collapse',)}
            ),
        )






funcTemp = lambda self: meaning_for_example(self)
funcTemp.admin_order_field = 'meaning'
funcTemp.short_description = u'Значение'
Example.meaning_for_example = funcTemp

funcTemp = lambda self: entry_for_example(self)
funcTemp.admin_order_field = 'meaning'
funcTemp.short_description = u'Лексема / Словосоч.'
Example.entry_for_example = funcTemp

EXAMPLE_FIELDSETS = (
        (None, {'fields': (('example', 'context'), 'address_text', 'greek_eq_status')}),
        (u'Примечание к примеру', {'fields': ('additional_info', 'note'), 'classes': ('collapse',)}),
    )

class Example_Inline(admin.StackedInline):
    model = Example
    extra = 1
    fieldsets = EXAMPLE_FIELDSETS
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }

class AdminExample(admin.ModelAdmin):
    inlines = (GreekEquivalentForExample_Inline,)
    raw_id_fields = ('meaning',)
    fieldsets = ((None, {'fields': ('meaning',), 'classes': ('hidden',)}),) + EXAMPLE_FIELDSETS
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }
    ordering = ('-id',)
    list_display = ('entry_for_example', 'meaning_for_example', 'id', 'example', 'address_text', 'greek_eq_status')
    list_display_links = ('id', 'example')
    list_editable = ('greek_eq_status', 'address_text')
    list_filter = (FirstVolumeExampleFilter, 'greek_eq_status',)
    search_fields = (
        'example',
        'address_text',
        'meaning__meaning',
        'meaning__gloss',
        'meaning__entry_container__civil_equivalent',
        'meaning__entry_container__orthographic_variants__idem',
        'meaning__collogroup_container__collocation_set__civil_equivalent',
        'meaning__collogroup_container__collocation_set__collocation',
        )
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminExample.has_add_permission = staff_has_permission
AdminExample.has_change_permission = staff_has_permission
AdminExample.has_delete_permission = staff_has_permission

admin.site.register(Example, AdminExample)
ui.register(Example, AdminExample)




class MeaningContext_Inline(admin.StackedInline):
    model = MeaningContext
    extra = 0
    fieldsets = ((None, {'fields': ('context', ('left_text', 'right_text'),)}),)




Meaning._entry = host_entry
Meaning._collogroup = host_collogroup
Meaning._parent_meaning = parent_meaning
class AdminMeaning(admin.ModelAdmin):
    inlines = (
        MeaningContext_Inline,
        Example_Inline,
        )
    raw_id_fields = (
        'entry_container',
        'collogroup_container',
        'link_to_entry',
        'link_to_collogroup',
        'link_to_meaning',
        'cf_entries',
        'cf_collogroups',
        'cf_meanings'
    )
    fieldsets = (
            (u'То, к чему значение относится',
                {'fields': (('entry_container', 'collogroup_container'), 'parent_meaning'),
                 'classes': ('hidden',)}),
            (u'См.',
                {'fields': (('link_to_entry', 'link_to_collogroup'), 'link_to_meaning'),
                'classes': ('collapse',)}),
            (u'Ср.',
                {'fields': (('cf_entries', 'cf_collogroups'), 'cf_meanings'),
                'classes': ('collapse',)}),
            (u'В роли сущ.',
                {'fields': ('substantivus', 'substantivus_type'),
                'classes': ('collapse',)}),
            (None,
                {'fields': ('metaphorical', 'figurative', 'is_valency')}),
            (None,
                {'fields': ('meaning', 'gloss')}),
            (None, { 'fields': tuple(), 'classes': ('blank',) }),
            (u'Примечание к значению',
                {'fields': ('additional_info',),
                'classes': ('collapse',)}),
        )
    save_on_top = True
    formfield_overrides = {
        models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})},
        }
    filter_horizontal = ('cf_entries', 'cf_collogroups', 'cf_meanings')
    ordering = ('-id',)
    list_display = (
        'id',
        '_entry',
        '_collogroup',
        '_parent_meaning',
        'metaphorical',
        'figurative',
        'substantivus',
        'is_valency',
        'transitivity',
        'meaning_for_admin',
        'examples_for_admin',
    )
    list_display_links = ('id',)
    list_editable = (
        'metaphorical',
        'figurative',
        'substantivus',
        'is_valency',
        'transitivity',
    )
    list_filter = (
        FirstVolumeMeaningFilter,
        'metaphorical',
        'figurative',
        SubstantivusMeaningFilter,
        'is_valency',
        'transitivity',
    )
    search_fields = (
        #'entry_container__civil_equivalent',
        #'entry_container__orthographic_variants__idem',
        #'collogroup_container__collocation_set__civil_equivalent',
        #'collogroup_container__collocation_set__collocation',
        'meaning',
        'gloss',
        )
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminMeaning.has_add_permission = staff_has_permission
AdminMeaning.has_change_permission = staff_has_permission
AdminMeaning.has_delete_permission = staff_has_permission

class AdminMeaningUI(AdminMeaning):
    pass
AdminMeaningUI.fieldsets = copy.deepcopy(AdminMeaning.fieldsets)
AdminMeaningUI.fieldsets = AdminMeaningUI.fieldsets[0:1] + AdminMeaningUI.fieldsets[3:]

admin.site.register(Meaning, AdminMeaning)
ui.register(Meaning, AdminMeaningUI)




class Participle_Inline(admin.StackedInline):
    model = Participle
    extra = 1
    fieldsets = ((None, { 'fields': ('tp', 'idem') }),)




Entry.__unicode__ = lambda self: entry_with_orth_variants(self)
Entry.entry_authors = lambda self: u', '.join([a.__unicode__() for a in
                                               self.authors.all()])
hmap = {
    1: u'\u00b9',
    2: u'\u00b2',
    3: u'\u00b3',
    4: u'\u2074',
    None: u'',
}
def headword(self):
    return u'''<i>%s</i> <span class="cslav">%s</span><span
                style="font-size: larger">%s</span><span
                style="font-size: smaller">%s</span>''' % (
        self.get_part_of_speech_display(),
        self.orth_vars[0].idem_ucs,
        hmap[self.homonym_order],
        u'<br>%s' % self.homonym_gloss if self.homonym_gloss else u'',
        )
headword.short_description = u''  # Делаем заголовок столбца пустым
headword.admin_order_field = 'civil_equivalent'
headword.allow_tags = True
Entry.headword = headword

def civil_inv(self):
    return self.civil_inverse
civil_inv.short_description = u''  # Делаем заголовок столбца пустым
civil_inv.admin_order_field = 'civil_inverse'
Entry.civil_inv = civil_inv

entry_actions = []
def assign_author(author):
    def func(modeladmin, request, queryset):
        for entry in queryset:
            entry.authors.add(author)
    func.short_description = u'Назначить выбранные статьи автору %s' % author
    func.func_name = 'assign_author_%s' % author.pk
    return func
for author in CustomUser.objects.all():#.filter(groups__name=u'authors'):
    entry_actions.append(assign_author(author))

class AdminEntry(admin.ModelAdmin):
    raw_id_fields = (
        'derivation_entry',
        'link_to_entry',
        'link_to_collogroup',
        'link_to_meaning',
        'cf_entries',
        'cf_collogroups',
        'cf_meanings',
    )
    fieldsets = (
        (None, {
            'fields': (('untitled_exists', 'reconstructed_headword',
                'questionable_headword'),),
            }),
        (None, {
            'fields': ('civil_equivalent',),
            }),
        (u'Омонимия', {
            'fields': ('homonym_order', 'homonym_gloss'),
            'classes': ('collapse',) } ),
        (None, {
            'fields': ('part_of_speech',),
            }),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (None, { # Для сущ. и прил.
            'fields': ('uninflected',),
            'classes': ('hidden noun adjective',) } ),
        (None, { # Для сущ.
            'fields': ('genitive', 'gender', 'tantum'),
            'classes': ('hidden noun',) } ),
        (None, { # Для имен собств.
            'fields': ('onym', 'canonical_name', 'nom_sg'),
            'classes': ('hidden noun',) } ),
        (None, { # Для прил.
            'fields': ('short_form', 'possessive'),
            'classes': ('hidden adjective',) } ),
        (None, { # Для глаг.
            'fields': ('sg1', 'sg2'),
            'classes': ('hidden verb',) } ),
        (None, { # Для прич.
            'fields': ('participle_type',),
            'classes': ('hidden participle',) } ),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (None, { 'fields': ('derivation_entry',) }),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (u'См.',
            {'fields': ('link_to_entry', 'link_to_collogroup', 'link_to_meaning'),
            'classes': ('collapse',)}),
        (u'Ср.',
            {'fields': ('cf_entries', 'cf_collogroups', 'cf_meanings'),
            'classes': ('collapse',)}),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (u'Примечание к статье', {
            'fields':  ('additional_info',),
            'classes': ('collapse',) }),
        (None, { 'fields': tuple(), 'classes': ('blank',) }),
        (None, { 'fields': ('status',) }),
        )
    inlines = (
        OrthVar_Inline,
        Participle_Inline,
        Etymology_Inline,
        )
    list_display = (
        'civil_inv',
        'headword',
        'untitled_exists',
        'part_of_speech',
        'genitive',
        'short_form',
        'sg1',
        'sg2',
        )
    list_display_links = (
        'headword',
        )
    list_filter = (
    	FirstVolumeEntryFilter,
        'authors',
        'status',
        'part_of_speech',
        'uninflected',
        'gender',
        'tantum',
        'onym',
        'canonical_name',
        'possessive',
        'transitivity',
        'participle_type',
        )
    list_editable = (
        'untitled_exists',
        'part_of_speech',
        'genitive',
        'short_form',
        'sg1',
        'sg2',
        )
    actions = entry_actions
    search_fields = ('civil_equivalent',)# 'orthographic_variants__idem')
    # При переходе к моделям, соотносящимся с основной как "много к одному"
    # в результатах поиска возможны дубликаты.
    # См. http://code.djangoproject.com/ticket/15839

    filter_horizontal = ('cf_entries', 'cf_collogroups', 'cf_meanings')
    ordering = ('civil_equivalent',)#'civil_inverse',)
    save_on_top = True
    formfield_overrides = { models.TextField: {'widget': forms.Textarea(attrs={'rows':'2'})}, }
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminEntry.has_add_permission = staff_has_permission
AdminEntry.has_change_permission = staff_has_permission
AdminEntry.has_delete_permission = superuser_has_permission


class AdminEntryADMIN(AdminEntry):
    pass

AdminEntryADMIN.fieldsets = copy.deepcopy(AdminEntry.fieldsets)
AdminEntryADMIN.fieldsets[-1][1]['fields'] = ('authors', 'status', 'antconc_query')

class AdminEntryUI(AdminEntry):
    pass

AdminEntryUI.fieldsets = AdminEntry.fieldsets[:14] + AdminEntry.fieldsets[16:]

admin.site.register(Entry, AdminEntryADMIN)
ui.register(Entry, AdminEntryUI)




#class AdminCollocation(admin.ModelAdmin):
#    inlines = (EtymologyForCollocation_Inline,)
#    fieldsets = (
#            (None, {'fields': ('collocation', 'civil_equivalent')}),
#        )
#    class Media:
#        css = {"all": ("fix_admin.css",)}
#        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
#    def response_add(self, request, obj, post_url_continue='/'):
#        post_url_continue = obj.host_entry.get_absolute_url()
#        return HttpResponseRedirect(post_url_continue + 'intermed/')
#    def response_change(self, request, obj):
#        post_url_continue = obj.host_entry.get_absolute_url()
#        return HttpResponseRedirect(post_url_continue + 'intermed/')
#
#AdminCollocation.has_add_permission = staff_has_permission
#AdminCollocation.has_change_permission = staff_has_change_permission
#AdminCollocation.has_delete_permission = staff_has_delete_permission
#
#admin.site.register(Collocation, AdminCollocation)
#ui.register(Collocation, AdminCollocation)

class Collocation_Inline(admin.StackedInline):
    model = Collocation
    extra = 1
    fieldsets = (
            (None, {'fields': ('collocation', 'civil_equivalent', 'order')}),
        )




CollocationGroup.__unicode__=lambda self: _collocations(self)
CollocationGroup._entry = host_entry
class AdminCollocationGroup(admin.ModelAdmin):
    inlines = (Collocation_Inline,)
    raw_id_fields = (
        'base_meaning',
        'base_entry',
        'link_to_entry',
        'link_to_meaning',
        'cf_entries',
        'cf_meanings',
    )
    fieldsets = (
            (None,
                {'fields': (('base_meaning', 'base_entry'),),
                'classes': ('hidden',)}),
            (u'См.',
                {'fields': ('link_to_entry', 'link_to_meaning'),
                'classes': ('collapse',)}),
            (u'Ср.',
                {'fields': ('cf_entries', 'cf_meanings'),
                'classes': ('collapse',)}),
            (None, {'fields': (('phraseological',),) }),
        )
    ordering = ('collocation_set__collocation',)
    filter_horizontal = ('cf_entries', 'cf_meanings')
    list_display = (
        'id',
        '_entry',
        'phraseological',
        '__unicode__',
        'meanings_for_admin',
        'examples_for_admin',
    )
    list_display_links = ('id', '__unicode__')
    list_editable = ('phraseological',)
    list_filter = (FirstVolumeCollogroupFilter, 'phraseological',)
    search_fields = ('collocation_set__civil_equivalent', 'collocation_set__collocation')
    class Media:
        css = {"all": ("fix_admin.css",)}
        js = ("js/libs/ac2ucs8.js", "fix_admin.js",)
    def response_add(self, request, obj, post_url_continue='/'):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')
    def response_change(self, request, obj):
        post_url_continue = obj.host_entry.get_absolute_url()
        return HttpResponseRedirect(post_url_continue + 'intermed/')

AdminCollocationGroup.has_add_permission = staff_has_permission
AdminCollocationGroup.has_change_permission = staff_has_permission
AdminCollocationGroup.has_delete_permission = staff_has_permission

class AdminCollocationGroupUI(AdminCollocationGroup):
    pass
AdminCollocationGroupUI.fieldsets = copy.deepcopy(AdminCollocationGroup.fieldsets)
AdminCollocationGroupUI.fieldsets = AdminCollocationGroupUI.fieldsets[0:1]

admin.site.register(CollocationGroup, AdminCollocationGroup)
ui.register(CollocationGroup, AdminCollocationGroupUI)
