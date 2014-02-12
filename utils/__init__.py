# -*- coding: utf-8 -*-
import cmd
import re

from slavdict.dictionary.models import Example as _Example

class DataChangeShell(cmd.Cmd):
    intro = 'Slavdict shell for data change :)\n'
    prompt = '> '

    def __init__(self, model=_Example, attrname='address_text'):
        cmd.Cmd.__init__(self)
        self.state = 'find'
        self.model = model
        self.attrname = attrname
        self.intro = self.intro + '%s().%s\n' % (self.model.__name__,
                                                 self.attrname)
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
        print u'\nfind: %s\nreplace: %s\n' % (self.pattern.pattern, self.replacement)

    def do_find(self, arg):
        count = 0
        for item in self.model.objects.all():
            if self.pattern.search(getattr(item, self.attrname)):
                print getattr(item, self.attrname)
                count += 1
        print u'\n%s\n%i\n' % (self.pattern.pattern, count)

    def do_try(self, arg):
        count = 0
        for item in self.model.objects.all():
            if self.pattern.search(getattr(item, self.attrname)):
                initial = getattr(item, self.attrname)
                final = self.pattern.sub(self.replacement, initial)
                count += 1
                print u'%s\n%s\n' % (initial, final)
        print u'\n? %s --> %s ?\n%i\n' % (self.pattern.pattern, self.replacement, count)

    def do_replace(self, arg):
        count = 0
        for item in self.model.objects.all():
            if self.pattern.search(getattr(item, self.attrname)):
                initial = getattr(item, self.attrname)
                final = re.sub(self.pattern, self.replacement, initial)
                setattr(item, self.attrname, final)
                item.save(without_mtime=True)
                count += 1
                print u'%s\n%s\n' % (initial, final)
        print u'\n! %s --> %s !\n%i\n' % (self.pattern.pattern, self.replacement, count)


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
                self.onecmd('pattern %s' % arg)
                self.onecmd('find')
            elif self.state == 'replace':
                self.onecmd('replacement %s' % arg)
                self.onecmd('try')

    def emptyline(self):
        if self.state == 'find':
            self.onecmd('find')
        elif self.state == 'replace':
            self.onecmd('try')
