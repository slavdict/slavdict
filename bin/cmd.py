import cmd
import math
import os
import re
import subprocess
import sys
import tempfile

from collections import defaultdict

from django.db import transaction
from django.db.models import Model
from django.db.models.fields import TextField, CharField

import slavdict.dictionary.models as models
from slavdict.dictionary.models import *
from slavdict.csl_annotations.models import *

EDITOR = os.environ.get('EDITOR', 'vi')
INDEXES = {1: '¹', 2: '²', 3: '³'}
TRY_OR_REPLACE_COMMAND = ('.', '/')
CANCEL_COMMANDS = ('..', '//')
EDIT_COMMANDS = ('.edit', 'эээ')
SORT_COMMANDS = ('.sort',)
VERBOSE_COMMANDS = ('.verbose',)

CSI = '\033['
HIDE_CURSOR = CSI + '?25l'
SHOW_CURSOR = CSI + '?25h'
ERASE_LINE = CSI + '2K'
ERASE_LINEEND = CSI + '0K'
MOVE_CURSOR_UP = CSI + '%iA'  # шаблон для подстановки числа шагов
SAVE_CURSOR_POSITION = CSI + 's'
RESTORE_CURSOR_POSITION = CSI + 'u'

RESET_FORMAT = CSI + '0m'
BOLD_BLACK = CSI + '1;30m'
BOLD_CYAN = CSI + '1;36m'
BOLD_GREEN = CSI + '1;32m'
BOLD_RED = CSI + '1;31m'
BOLD_YELLOW = CSI + '1;33m'
RED = CSI + '0;31m'
GREEN = CSI + '0;32m'


def sort_by_entry(x):
    return x[1]

def sort_by_value(x):
    return x[2]


class DataChangeShell(cmd.Cmd):
    intro = 'Slavdict shell for data change :)'
    prompt = '> '

    def __init__(self, model_attrs=[(Example, ['address_text'])],
                 volumes=WHOLE_DICTIONARY):
        cmd.Cmd.__init__(self)
        self.volumes = volumes
        self.state = 'find'
        self.model_attrs = model_attrs
        self.intro = ('\n' + BOLD_YELLOW + self.intro + '\n\n' + GREEN +
                      '\n'.join('%s %s' % (model.__name__, attrs)
                                for model, attrs in self.model_attrs) +
                      RESET_FORMAT + '\n')
        self.pattern = re.compile('', re.UNICODE)
        self.replacement = None
        self.verbose = False
        self.sort_entries = True
        self.reset_found_items()
        self.change_prompt()

    def prepare(self, arg):
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

    # Основные команды

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
        print('\nfind: %s\nreplace: %s\n' % (self.pattern.pattern,
                                              self.replacement))

    def do_find(self, arg):
        try:
            if self.found_items:
                self._do_find2(arg)
            else:
                self._do_find(arg)
            print('\n   /%s/  %s %s%s\n' % (
                    BOLD_CYAN + self.pattern.pattern + RESET_FORMAT,
                    BOLD_YELLOW + str(
                        sum(sum(v.values()) for v in list(self.tcount.values()))
                    ) + RESET_FORMAT,
                    repr(self.tcount) if self.verbose else '',
                    ERASE_LINEEND,
                ))
        except (KeyboardInterrupt, Exception):
            sys.stdout.write(SHOW_CURSOR)
            print()
            import traceback
            traceback.print_exc()
            print('Поиск прерван...')
            # self.reset_found_items()

    def _do_find(self, arg):
        sys.stdout.write(HIDE_CURSOR)
        if self.sort_entries:
            sort_key = sort_by_entry
        else:
            sort_key = sort_by_value
        for model, attrs in self.model_attrs:
            self.tcount[model.__name__] = {}
            from_dict = model.__module__ == 'slavdict.dictionary.models'
            for attrname in attrs:
                storage_key = (model, attrname)
                items = model.objects.all()
                items_n = model.objects.count()
                count = 0
                sys.stdout.write('\n')
                mnote = '%s.%s' % (model.__name__, attrname)
                for i, item in enumerate(items):
                    note = '%s: %s, found: %s%s\r' % (
                        mnote,
                        BOLD_YELLOW + str(
                            int(math.ceil((i + 1) / items_n * 100))
                        ) + '%' + RESET_FORMAT,
                        BOLD_GREEN + str(count) + RESET_FORMAT,
                        ERASE_LINEEND,
                    )
                    sys.stdout.write(note)
                    if self.pattern.search(getattr(item, attrname) or ''):
                        if from_dict:
                            host_entry = item.host_entry
                            if not host_entry.is_in_volume(self.volumes):
                                continue
                        count += 1
                        txt = getattr(item, attrname) or ''
                        host_info = ''
                        if from_dict:
                            host_info = '%s%s' % (
                                    host_entry.civil_equivalent,
                                    INDEXES.get(host_entry.homonym_order, ''))
                            host = item.host
                            if host != host_entry:
                                host_info = '%s | %s' % (
                                              host_info, host.civil_equivalent)
                        value = (item, host_info, txt)
                        self.found_items[storage_key].append(value)
                self.found_items[storage_key] = list(
                        sorted(self.found_items[storage_key], key=sort_key))
                self.tcount[model.__name__][attrname] = count
                sys.stdout.write(MOVE_CURSOR_UP % 1 + '\r')
        sys.stdout.write(ERASE_LINE)
        sys.stdout.write(SHOW_CURSOR)
        self._do_find2(arg)

    def _do_find2(self, arg):
        for (model, attrname), items in list(self.found_items.items()):
            if items:
                print('\n%s.%s' % (
                        BOLD_YELLOW + model.__name__,
                        attrname + RESET_FORMAT + ERASE_LINEEND))
            for item, host_info, _ in items:
                txt = getattr(item, attrname) or ''
                host_info = BOLD_BLACK + host_info + RESET_FORMAT
                subst = self.pattern.sub(
                        BOLD_CYAN + r'\g<0>' + RESET_FORMAT, txt)
                if self.verbose:
                    print('*  %s\t%s' % (subst, host_info))
                else:
                    print('* ', subst)

    def do_try(self, arg):
        if self.replacement is None:
            print('Установите шаблон замены')
            return
        for (model, attrname), items in list(self.found_items.items()):
            if items:
                print('\n%s.%s' % (
                        BOLD_YELLOW + model.__name__,
                        attrname + RESET_FORMAT + ERASE_LINEEND))
            for item, host_info, _ in items:
                initial = getattr(item, attrname) or ''
                if self.pattern.search(initial):
                    try:
                        # NOTE:qSeF4: В шаблоне замены могут быть
                        # подстановочные знаки вроде \1, при том что
                        # в шаблоне поиска не будет никаких групп.
                        # Если подстрока для замены в этом случае
                        # будет найдена, то возникнет исключение.
                        self.pattern.sub(self.replacement, initial)
                    except re.error as err:
                        sys.stdout.write(SHOW_CURSOR)
                        self.replacement = None
                        print(('Шаблон замены сброшен '
                               'из-за несовместимости '
                               'с шаблоном поиска: %s' % err))
                        return
                    host_info = BOLD_BLACK + host_info + RESET_FORMAT
                    if self.verbose:
                        print('*  %s\n*  %s\n%s\n' % (
                            self.pattern.sub(
                                BOLD_CYAN + r'\g<0>' + RESET_FORMAT,
                                initial),
                            self.pattern.sub(
                                RED + self.replacement + RESET_FORMAT,
                                initial),
                            host_info,
                        ))
                    else:
                        print('*  %s\n*  %s\n' % (
                            self.pattern.sub(
                                BOLD_CYAN + r'\g<0>' + RESET_FORMAT,
                                initial),
                            self.pattern.sub(
                                RED + self.replacement + RESET_FORMAT,
                                initial),
                        ))
        print(('  ? %s --> %s ?   %s %s%s\n' % (
            BOLD_CYAN + self.pattern.pattern + RESET_FORMAT,
            BOLD_RED + self.replacement + RESET_FORMAT,
            BOLD_YELLOW + str(
                sum(sum(v.values()) for v in list(self.tcount.values()))
            ) + RESET_FORMAT,
            repr(self.tcount) if self.verbose else '',
            ERASE_LINEEND,
        )))

    def do_replace(self, arg):
        try:
            with transaction.atomic():
                self._do_replace(arg)
        except (KeyboardInterrupt, Exception):
            sys.stdout.write(SHOW_CURSOR)
            print()
            print('\n'.join(str(x) for x in sys.exc_info()[:]))
            print('Замена прервана. Все произведённые изменения отменены.')

    def _do_replace(self, arg):
        if self.replacement is None:
            print('Установите шаблон замены')
            return
        for (model, attrname), items in list(self.found_items.items()):
            from_dict = model.__module__ == 'slavdict.dictionary.models'
            if items:
                print('\n%s.%s' % (
                        BOLD_YELLOW + model.__name__,
                        attrname + RESET_FORMAT + ERASE_LINEEND))
            for item, host_info, _ in items:
                initial = getattr(item, attrname) or ''
                if self.pattern.search(initial):
                    try:  # SEE:qSeF4:
                        final = self.pattern.sub(self.replacement, initial)
                    except re.error as err:
                        sys.stdout.write(SHOW_CURSOR)
                        self.replacement = None
                        print(('Шаблон замены сброшен '
                               'из-за несовместимости '
                               'с шаблоном поиска: %s' % err))
                        return
                    setattr(item, attrname, final)
                    kwargs = { 'without_mtime': True } if from_dict else {}
                    item.save(**kwargs)
                    host_info = BOLD_BLACK + host_info + RESET_FORMAT
                    if self.verbose:
                        print('*  %s\n*  %s\n%s\n' % (
                            self.pattern.sub(
                                BOLD_CYAN + r'\g<0>' + RESET_FORMAT,
                                initial),
                            self.pattern.sub(
                                GREEN + self.replacement + RESET_FORMAT,
                                initial),
                            model.__name__, attrname, item.id, host_info,
                        ))
                    else:
                        print('*  %s\n*  %s\n' % (
                            self.pattern.sub(
                                BOLD_CYAN + r'\g<0>' + RESET_FORMAT, initial),
                            self.pattern.sub(
                                GREEN + self.replacement + RESET_FORMAT,
                                initial),
                        ))
        print(('  ! %s --> %s !   %s %s\n' % (
            BOLD_CYAN + self.pattern.pattern + RESET_FORMAT,
            BOLD_GREEN + self.replacement + RESET_FORMAT,
            BOLD_YELLOW + str(
                sum(sum(v.values()) for v in list(self.tcount.values()))
            ) + RESET_FORMAT,
            repr(self.tcount) if self.verbose else '',
        )))

    def do_edit_replace(self, arg):
        try:
            with transaction.atomic():
                self._do_edit_replace(arg)
        except (KeyboardInterrupt, Exception):
            sys.stdout.write(SHOW_CURSOR)
            print()
            print('\n'.join(str(x) for x in sys.exc_info()[:]))
            print('Замена прервана. Все произведённые изменения отменены.')
        else:
            print('''
            Правки внесены. Список отредактированных элементов ещё не сброшен.
            Пока шаблон поиска не изменён, можно ещё раз отредактировать
            тот же список с помощью комманд %s''' % ', '.join(
                    '"%s"' % c for c in EDIT_COMMANDS))

    def _do_edit_replace(self, arg):
        if not self.found_items:
            print('Нет элементов для правки')
            return
        TAB = '\u21b9'
        ENTER = '\u23ce'
        register = {}
        text = ''
        i = 1
        for (model, attrname), items in list(self.found_items.items()):
            from_dict = model.__module__ == 'slavdict.dictionary.models'
            text += '\n# %s.%s\n\n' % (model.__name__, attrname)
            for item, host_info, _ in items:
                register[i] = (item, attrname)
                if self.verbose:
                    text += '#\t%s\n' % host_info
                t = getattr(item, attrname) or ''
                t = re.sub(r'[\r\n\v]', ENTER, t)
                t = t.replace('\t', TAB)
                text += '%s\t%s\n' % (i, t)
                i += 1

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(text.encode('utf-8'))
            tf.flush()
            subprocess.call([EDITOR, tf.name])
            tf.seek(0)
            edited_lines = tf.read().decode('utf-8').split('\n')

        lines = [x for x in edited_lines if x.strip() and x[:1] != '#']
        for line in lines:
            oid, value = line.split('\t', 1)
            value = value.strip()
            value = value.replace(ENTER, '\n')
            value = value.replace(TAB, '\t')
            oid = int(oid)
            o, attrname = register.get(oid, (None, None))
            if o is not None:
                prev_value = getattr(o, attrname) or ''
                if value != prev_value:
                    setattr(o, attrname, value)
                    kwargs = { 'without_mtime': True } if from_dict else {}
                    o.save(**kwargs)
                    del register[oid]

    def default(self, arg):
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
        elif arg in SORT_COMMANDS:
            self.sort_entries = not self.sort_entries
            if self.sort_entries:
                print('Сортировка по статьям')
                sort_key = sort_by_entry
            else:
                print('Сортировка по значению')
                sort_key = sort_by_value
            for key, value in list(self.found_items.items()):
                self.found_items[key] = list(sorted(value, key=sort_key))
            self.onecmd('')
        else:
            if self.state == 'find':
                try:
                    self.onecmd('pattern %s' % arg)
                except re.error as err:
                    print('Шаблон поиска некорректен: %s' % err)
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


TEXT = '''
(Entry, [
    #'civil_equivalent',
    #'homonym_gloss',
    'nom_pl',
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
    #'context',
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
(Tip, [
    #'text'
]),


#
# Модели для аннотаций на портале «ЦСЛ сегодня»
#
(Author, [
    'first_name',
    'second_name',
    'last_name',
    'title',
]),
(TagGroup, [
    'name',
]),
(Tag, [
    'name',
]),
(Annotation, [
    'title',
    'bib',
    'annotation',
    'teaser',

    'anchor',
    'url',
    'youtube_id',
]),
    '''


def shell(model_attrs=None, volumes=WHOLE_DICTIONARY):
    if model_attrs is None:
        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(TEXT.encode('utf-8'))
            tf.flush()
            subprocess.call([EDITOR, tf.name])
            tf.seek(0)
            edited_text = tf.read().decode('utf-8')
        model_attrs = eval('[%s]' % edited_text, globals(), locals())
    DataChangeShell(model_attrs=model_attrs, volumes=volumes).cmdloop()


# Собрать все текстовые поля не самая хорошая идея, т.к. выпадающие списки
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
# shell(crazy_all)
