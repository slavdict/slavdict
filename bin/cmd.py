# -*- coding: utf-8 -*-
import cmd
import os
import re
import subprocess
import tempfile

from django.db.models import Model
from django.db.models.fields import TextField, CharField

import slavdict.dictionary.models as models
from slavdict.dictionary.models import Example as _Example

class DataChangeShell(cmd.Cmd):
    intro = 'Slavdict shell for data change :)\n'
    prompt = '> '

    def __init__(self, model_attrs=[(_Example, ['address_text'])],
                 first_volume=True):
        cmd.Cmd.__init__(self)
        self.first_volume = first_volume
        self.state = 'find'
        self.model_attrs = model_attrs
        self.intro = self.intro + '\n'.join(
                '%s %s' % (model.__name__, attrs)
                for model, attrs in self.model_attrs)
        self.pattern = re.compile('', re.UNICODE)
        self.replacement = None
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


    def do_quit(self, arg):
        return True

    def do_pattern(self, arg):
        self.pattern = re.compile(self.prepare(arg), re.UNICODE)

    def do_replacement(self, arg):
        self.replacement = self.prepare(arg)

    def do_show(self, arg):
        print u'\nfind: %s\nreplace: %s\n' % (self.pattern.pattern,
                                              self.replacement)

    def do_find(self, arg):
        tcount = {}
        for model, attrs in self.model_attrs:
            tcount[model.__name__] = {}
            for attrname in attrs:
                count = 0
                if self.first_volume:
                    items = (i for i in model.objects.all()
                               if i.host_entry.firs_volume)
                else:
                    items = models.objects.all()
                for item in items:
                    if self.pattern.search(getattr(item, attrname)):
                        txt = getattr(item, attrname)
                        print self.pattern.sub('\033[0;36m\g<0>\033[0m', txt)
                        count += 1
                tcount[model.__name__][attrname] = count
        print u'\n   /\033[1;36m%s\033[0m/  \033[1;33m%i\033[0m %r\n' % (
                self.pattern.pattern,
                sum(sum(v.values()) for v in tcount.values()),
                tcount,
                )

    def do_try(self, arg):
        if self.replacement is None:
            print u'Установите шаблон замены'
            return
        tcount = {}
        for model, attrs in self.model_attrs:
            tcount[model.__name__] = {}
            for attrname in attrs:
                count = 0
                if self.first_volume:
                    items = (i for i in model.objects.all()
                               if i.host_entry.firs_volume)
                else:
                    items = models.objects.all()
                for item in items:
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
                        count += 1
                        print u'%s\n%s\n' % (
                                self.pattern.sub('\033[0;36m\g<0>\033[0m', initial),
                                self.pattern.sub('\033[0;31m%s\033[0m' % self.replacement, initial))
                tcount[model.__name__][attrname] = count
        print (u'  ? \033[1;36m%s\033[0m --> \033[1;31m%s\033[0m ?   '
               u'\033[1;33m%i\033[0m %r\n' % (
                    self.pattern.pattern,
                    self.replacement,
                    sum(sum(v.values()) for v in tcount.values()),
                    tcount,
                    ))

    def do_replace(self, arg):
        if self.replacement is None:
            print u'Установите шаблон замены'
            return
        tcount = {}
        for model, attrs in self.model_attrs:
            tcount[model.__name__] = {}
            for attrname in attrs:
                count = 0
                if self.first_volume:
                    items = (i for i in model.objects.all()
                               if i.host_entry.firs_volume)
                else:
                    items = models.objects.all()
                for item in items:
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
                        count += 1
                        print u'%s\n%s\n' % (
                                self.pattern.sub('\033[0;36m\g<0>\033[0m', initial),
                                self.pattern.sub('\033[0;32m%s\033[0m' % self.replacement, initial))
                tcount[model.__name__][attrname] = count
        print (u'  ! \033[1;36m%s\033[0m --> \033[1;32m%s\033[0m !   '
               u'\033[1;33m%i\033[0m %r\n' % (
                    self.pattern.pattern,
                    self.replacement,
                    sum(sum(v.values()) for v in tcount.values()),
                    tcount,
                    ))


    def default(self, arg):
        arg = arg.decode('utf-8')
        if arg == 'EOF':
            return self.onecmd('quit')
        elif arg in ('.', '/'):
            if self.state == 'find':
                self.state = 'replace'
                if self.replacement is not None:
                    self.onecmd('try')
            elif self.state == 'replace':
                self.state = 'find'
                if self.replacement is not None:
                    self.onecmd('replace')
            self.change_prompt()
        elif arg in ('..', '//') and self.state == 'replace':
            self.state = 'find'
            self.change_prompt()
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
    'sg1',
    'sg2',
    #'additional_info',
    #'antconc_query',
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
    #'additional_info',
]),
(Example, [
    'example',
    'address_text',
    'note',
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

def shell():
    from slavdict.dictionary.models import *
    EDITOR = os.environ.get('EDITOR','vi')
    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(TEXT.encode('utf-8'))
        tf.flush()
        subprocess.call([EDITOR, tf.name])
        tf.seek(0)
        edited_text = tf.readlines()
    model_attrs = eval(u'[%s]' % edited_text, locals=locals())
    DataChangeShell(model_attrs=model_attrs, first_volume=True).cmdloop()

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
