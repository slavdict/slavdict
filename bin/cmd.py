# -*- coding: utf-8 -*-
import cmd
import os
import re
import subprocess
import tempfile

from collections import defaultdict

from django.db import transaction
from django.db.models import Model
from django.db.models.fields import TextField, CharField

import slavdict.dictionary.models as models
from slavdict.dictionary.models import *

EDITOR = os.environ.get('EDITOR','vi')
INDEXES = {1: u'¹', 2: u'²', 3: u'³'}
TRY_OR_REPLACE_COMMAND = ('.', '/')
CANCEL_COMMANDS = ('..', '//')
EDIT_COMMANDS = (u'.edit', u'эээ')
VERBOSE_COMMANDS = (u'.verbose',)

class DataChangeShell(cmd.Cmd):
    intro = 'Slavdict shell for data change :)\n'
    prompt = '> '

    def __init__(self, model_attrs=[(Example, ['address_text'])],
                 volumes=WHOLE_DICTIONARY):
        cmd.Cmd.__init__(self)
        self.volumes = volumes
        self.state = 'find'
        self.model_attrs = model_attrs
        self.intro += '\n'.join('%s %s' % (model.__name__, attrs)
                                for model, attrs in self.model_attrs)
        self.pattern = re.compile('', re.UNICODE)
        self.replacement = None
        self.verbose = False
        self.reset_found_items()
        self.change_prompt()


    def prepare(self, arg):
        if isinstance(arg, str):
            arg = arg.decode('utf-8')
        if arg.startswith('--'):
            arg = arg[2:]
        if arg.endswith('--'):
            arg = arg[:-2]
        return arg

    def change_prompt(self):
        self.prompt = self.state + DataChangeShell.prompt

    def reset_found_items(self):
        self.found_items = defaultdict(list)
        self.tcount = {}


    def do_quit(self, arg):
        return True

    def do_pattern(self, arg):
        prepared_arg = self.prepare(arg)
        if self.pattern.pattern != prepared_arg:
            self.pattern = re.compile(prepared_arg, re.UNICODE)
            self.reset_found_items()

    def do_replacement(self, arg):
        self.replacement = self.prepare(arg)

    def do_show(self, arg):
        print u'\nfind: %s\nreplace: %s\n' % (self.pattern.pattern,
                                              self.replacement)

    def do_find(self, arg):
        try:
            if self.found_items:
                self._do_find2(arg)
            else:
                self._do_find(arg)
            print u'\n   /\033[1;36m%s\033[0m/  \033[1;33m%i\033[0m %s\n' % (
                    self.pattern.pattern,
                    sum(sum(v.values()) for v in self.tcount.values()),
                    repr(self.tcount) if self.verbose else '',
                    )
        except (KeyboardInterrupt, Exception) as e:
            print
            print type(e).__name__
            print u'Поиск прерван...'
            #self.reset_found_items()

    def _do_find(self, arg):
        for model, attrs in self.model_attrs:
            self.tcount[model.__name__] = {}
            for attrname in attrs:
                count = 0
                items = (i for i in model.objects.all()
                           if i.host_entry.volume(self.volumes))
                print u'\n\033[1;33m%s.%s\033[0m' % (model.__name__, attrname)
                for item in items:
                    if self.pattern.search(getattr(item, attrname)):
                        txt = getattr(item, attrname)
                        host = item.host
                        host_entry = item.host_entry
                        host_info = u'%s%s' % (
                                host_entry.civil_equivalent,
                                INDEXES.get(host_entry.homonym_order, u''))
                        if host != host_entry:
                            host_info = u'%s | %s' % (
                                              host_info, host.civil_equivalent)
                        host_info = u'\033[1;30m%s\033[0m' % host_info
                        subst = self.pattern.sub('\033[0;36m\g<0>\033[0m', txt)
                        if self.verbose:
                            print u'*  %s\t%s' % (subst, host_info)
                        else:
                            print u'* ', subst
                        count += 1
                        key = (model, attrname)
                        value = (item, host, host_entry)
                        self.found_items[key].append(value)
                self.tcount[model.__name__][attrname] = count

    def _do_find2(self, arg):
        for (model, attrname), items in self.found_items.items():
            print u'\n\033[1;33m%s.%s\033[0m' % (model.__name__, attrname)
            for item, host, host_entry in items:
                txt = getattr(item, attrname)
                host_info = u'%s%s' % (
                                host_entry.civil_equivalent,
                                INDEXES.get(host_entry.homonym_order, u''))
                if host != host_entry:
                    host_info = u'%s | %s' % (host_info, host.civil_equivalent)
                host_info = u'\033[1;30m%s\033[0m' % host_info
                subst = self.pattern.sub('\033[0;36m\g<0>\033[0m', txt)
                if self.verbose:
                    print u'*  %s\t%s' % (subst, host_info)
                else:
                    print u'* ', subst

    def do_try(self, arg):
        if self.replacement is None:
            print u'Установите шаблон замены'
            return
        for (model, attrname), items in self.found_items.items():
            print u'\n\033[1;33m%s.%s\033[0m' % (model.__name__, attrname)
            for item, host, host_entry in items:
                if self.pattern.search(getattr(item, attrname)):
                    initial = getattr(item, attrname)
                    try:
                        # NOTE:qSeF4: В шаблоне замены могут быть
                        # подстановочные знаки вроде \1, при том что
                        # в шаблоне поиска не будет никаких групп.
                        # Если подстрока для замены в этом случае
                        # будет найдена, то возникнет исключение.
                        self.pattern.sub(self.replacement, initial)
                    except re.error as err:
                        self.replacement = None
                        print (u'Шаблон замены сброшен '
                               u'из-за несовместимости '
                               u'с шаблоном поиска: %s' % err)
                        return
                    host_info = u'%s%s' % (
                                    host_entry.civil_equivalent,
                                    INDEXES.get(host_entry.homonym_order, u''))
                    if host != host_entry:
                        host_info = u'%s | %s' % (host_info, host.civil_equivalent)
                    host_info = u'\033[1;30m%s\033[0m' % host_info
                    if self.verbose:
                        print u'*  %s\n*  %s\n%s\n' % (
                            self.pattern.sub('\033[0;36m\g<0>\033[0m', initial),
                            self.pattern.sub('\033[0;31m%s\033[0m' % self.replacement, initial),
                            host_info)
                    else:
                        print u'*  %s\n*  %s\n' % (
                            self.pattern.sub('\033[0;36m\g<0>\033[0m', initial),
                            self.pattern.sub('\033[0;31m%s\033[0m' % self.replacement, initial))
        print (u'  ? \033[1;36m%s\033[0m --> \033[1;31m%s\033[0m ?   '
               u'\033[1;33m%i\033[0m %s\n' % (
                    self.pattern.pattern,
                    self.replacement,
                    sum(sum(v.values()) for v in self.tcount.values()),
                    repr(self.tcount) if self.verbose else '',
                    ))

    def do_replace(self, arg):
        try:
            with transaction.atomic():
                self._do_replace(arg)
        except KeyboardInterrupt, Exception:
            print
            print u'\n'.join(sys.exc_info()[:])
            print u'Замена прервана. Все произведённые изменения отменены.'

    def _do_replace(self, arg):
        if self.replacement is None:
            print u'Установите шаблон замены'
            return
        for (model, attrname), items in self.found_items.items():
            print u'\n\033[1;33m%s.%s\033[0m' % (model.__name__, attrname)
            for item, host, host_entry in items:
                if self.pattern.search(getattr(item, attrname)):
                    initial = getattr(item, attrname)
                    try:  # SEE:qSeF4:
                        final = self.pattern.sub(self.replacement, initial)
                    except re.error as err:
                        self.replacement = None
                        print (u'Шаблон замены сброшен '
                               u'из-за несовместимости '
                               u'с шаблоном поиска: %s' % err)
                        return
                    setattr(item, attrname, final)
                    item.save(without_mtime=True)
                    host_info = u'%s%s' % (
                                    host_entry.civil_equivalent,
                                    INDEXES.get(host_entry.homonym_order, u''))
                    if host != host_entry:
                        host_info = u'%s | %s' % (host_info, host.civil_equivalent)
                    host_info = u'\033[1;30m%s\033[0m' % host_info
                    if self.verbose:
                        print u'*  %s\n*  %s\n%s\n' % (
                            self.pattern.sub('\033[0;36m\g<0>\033[0m', initial),
                            self.pattern.sub('\033[0;32m%s\033[0m' % self.replacement, initial),
                            model.__name__, attrname, item.id, host_info)
                    else:
                        print u'*  %s\n*  %s\n' % (
                            self.pattern.sub('\033[0;36m\g<0>\033[0m', initial),
                            self.pattern.sub('\033[0;32m%s\033[0m' % self.replacement, initial))
        print (u'  ! \033[1;36m%s\033[0m --> \033[1;32m%s\033[0m !   '
               u'\033[1;33m%i\033[0m %s\n' % (
                    self.pattern.pattern,
                    self.replacement,
                    sum(sum(v.values()) for v in self.tcount.values()),
                    repr(self.tcount) if self.verbose else '',
                    ))

    def do_edit_replace(self, arg):
        try:
            with transaction.atomic():
                self._do_edit_replace(arg)
        except KeyboardInterrupt, Exception:
            print
            print u'\n'.join(sys.exc_info()[:])
            print u'Замена прервана. Все произведённые изменения отменены.'
        else:
            print u'''
            Правки внесены. Список отредактированных элементов ещё не сброшен.
            Пока шаблон поиска не изменён, можно ещё раз отредактировать
            тот же список с помощью комманд %s''' % u', '.join(
                    u'"%s"' % c for c in EDIT_COMMANDS)

    def _do_edit_replace(self, arg):
        if not self.found_items:
            print u'Нет элементов для правки'
            return
        register = {}
        text = u''
        i = 1
        for (model, attrname), items in self.found_items.items():
            text += u'\n# %s.%s\n\n' % (model.__name__, attrname)
            for item, host, host_entry in items:
                host_info = u'%s%s' % (host_entry.civil_equivalent,
                                INDEXES.get(host_entry.homonym_order, u''))
                if host != host_entry:
                    host_info = u'%s  <  %s' % (host.civil_equivalent, host_info)
                register[i] = (item, attrname)
                if self.verbose:
                    text += u'#\t%s\n' % host_info
                text += u'%s\t%s\n' % (i, getattr(item, attrname))
                i += 1

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(text.encode('utf-8'))
            tf.flush()
            subprocess.call([EDITOR, tf.name])
            tf.seek(0)
            edited_text = tf.readlines()

        lines = filter(lambda x:x.strip() and x[:1] != '#', edited_text)
        for line in lines:
            oid, value = line.decode('utf-8').strip().split(u'\t', 1)
            oid = int(oid)
            o, attrname = register.get(oid, (None, None))
            if o is not None:
                prev_value = getattr(o, attrname)
                if value != prev_value:
                    setattr(o, attrname, value)
                    o.save(without_mtime=True)
                    del register[oid]


    def default(self, arg):
        arg = arg.decode('utf-8')
        if arg == 'EOF':
            return self.onecmd('quit')
        elif arg in TRY_OR_REPLACE_COMMAND:
            if self.state == 'find':
                self.state = 'replace'
                if self.replacement is not None:
                    self.onecmd('try')
            elif self.state == 'replace':
                self.state = 'find'
                if self.replacement is not None:
                    self.onecmd('replace')
            self.change_prompt()
        elif arg in CANCEL_COMMANDS and self.state == 'replace':
            self.state = 'find'
            self.change_prompt()
        elif arg in EDIT_COMMANDS:
            self.state = 'find'
            self.onecmd('edit_replace')
        elif arg in VERBOSE_COMMANDS:
            self.verbose = not self.verbose
            self.onecmd('')
        else:
            if self.state == 'find':
                try:
                    self.onecmd('pattern %s' % arg)
                except re.error as err:
                    print u'Шаблон поиска некорректен: %s' % err
                else:
                    self.onecmd('find')
            elif self.state == 'replace':
                self.onecmd('replacement %s' % arg)
                self.onecmd('try')

    def emptyline(self):
        if self.state == 'find':
            self.onecmd('find')
        elif self.state == 'replace':
            self.onecmd('try')

TEXT = u'''
(Entry, [
    #'civil_equivalent',
    #'homonym_gloss',
    'nom_sg',
    'short_form',
    'genitive',
    'sg1',
    'sg2',
    #'additional_info',
    #'antconc_query',
    #'word_forms_list',
]),
(Etymology, [
    'text',
    'unitext',
    'translit',
    'meaning',
    'gloss',
    'source',
    'mark',
    #'additional_info',
]),
(MeaningContext, [
    'left_text',
    'context',
    'right_text',
]),
(Meaning, [
    'meaning',
    'gloss',
    #'substantivus_csl',
    #'additional_info',
]),
(Example, [
    'example',
    'address_text',
    'note',
    #'additional_info',
]),
(Translation, [
    'translation',
    'additional_info',
]),
(CollocationGroup, [
    #'additional_info',
]),
(Collocation, [
    'collocation',
    #'civil_equivalent',
]),
(GreekEquivalentForExample, [
    'unitext',
    'mark',
    'source',
    #'initial_form',
    #'initial_form_phraseology',
    'note',
    #'additional_info',
]),
(OrthographicVariant, [
    'idem',
    'use',
]),
(Participle, [
    'idem',
]),
    '''

def shell(model_attrs=None, volumes=WHOLE_DICTIONARY):
    if model_attrs is None:
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(TEXT.encode('utf-8'))
            tf.flush()
            subprocess.call([EDITOR, tf.name])
            tf.seek(0)
            edited_text = tf.read()
        model_attrs = eval(u'[%s]' % edited_text, globals(), locals())
    DataChangeShell(model_attrs=model_attrs, volumes=volumes).cmdloop()

# Собрать все текстовые поля не самая хорошая идея, т.к.  выпадающие списки
# тоже сохраняются в текстовых полях. Тем не менее, вот как это можно сделать:
crazy_all = []
for identifier in models.__dict__:
    x = models.__dict__[identifier]
    if isinstance(x, type) and issubclass(x, Model):
        fieldnames = []
        for i in x._meta.fields:
            if isinstance(i, (TextField, CharField)):
                fieldnames.append(i.name)
        if fieldnames:
            crazy_all.append((x, fieldnames))
#shell(crazy_all)
