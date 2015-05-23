# -*- coding: utf-8 -*-
import cmd
import re

from slavdict.dictionary.models import Example as _Example

class DataChangeShell(cmd.Cmd):
    intro = 'Slavdict shell for data change :)\n'
    prompt = '> '

    def __init__(self, model_attrs=[(_Example, ['address_text'])]):
        cmd.Cmd.__init__(self)
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
                for item in model.objects.all():
                    if self.pattern.search(getattr(item, attrname)):
                        print getattr(item, attrname)
                        count += 1
                tcount[model.__name__][attrname] = count
        print u'\n  %r\n  \033[0;31m%i\033[0m   %s\n' % (
                tcount, sum(sum(v.values()) for v in tcount.values()),
                self.pattern.pattern,
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
                for item in model.objects.all():
                    if self.pattern.search(getattr(item, attrname)):
                        initial = getattr(item, attrname)
                        try:
                            # NOTE:qSeF4: В шаблоне замены могут быть
                            # подстановочные знаки вроде \1, при том что
                            # в шаблоне поиска не будет никаких групп.
                            # Если подстрока для замены в этом случае
                            # будет найдена, то возникнет исключение.
                            final = self.pattern.sub(self.replacement, initial)
                        except re.error as err:
                            self.replacement = None
                            print (u'Шаблон замены сброшен '
                                   u'из-за несовместимости '
                                   u'с шаблоном поиска: %s' % err)
                            return
                        count += 1
                        print u'%s\n%s\n' % (initial, final)
                tcount[model.__name__][attrname] = count
        print u'\n  %r\n  \033[0;31m%i\033[0m   ? %s --> %s ?\n' % (
                tcount, sum(sum(v.values()) for v in tcount.values()),
                self.pattern.pattern, self.replacement,
                )

    def do_replace(self, arg):
        if self.replacement is None:
            print u'Установите шаблон замены'
            return
        tcount = {}
        for model, attrs in self.model_attrs:
            tcount[model.__name__] = {}
            for attrname in attrs:
                count = 0
                for item in model.objects.all():
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
                        print u'%s\n%s\n' % (initial, final)
                tcount[model.__name__][attrname] = count
        print u'\n  %r\n  \033[0;31m%i\033[0m   ? %s --> %s ?\n' % (
                tcount, sum(sum(v.values()) for v in tcount.values()),
                self.pattern.pattern, self.replacement,
                )


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

def shell(model_attrs=[(_Example, ['address_text'])]):
    DataChangeShell(model_attrs=model_attrs).cmdloop()
