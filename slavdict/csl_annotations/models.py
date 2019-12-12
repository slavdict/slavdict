import markdown

from django.db import models
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.utils.safestring import mark_safe


class FixedWidthTextField(CharField):
    pass


TAG_CATEGORIES = (
    ('a', 'Этап'),
    ('e', 'Регион'),
    ('i', 'Тексты'),
    ('m', 'Книга'),
    ('q', 'Материал'),
    ('u', 'Инструменты'),
)
TAG_COLORS = {}
TAG_COLORS[TAG_CATEGORIES[0][0]] = '#f60000'
TAG_COLORS[TAG_CATEGORIES[1][0]] = '#ff8c00'
TAG_COLORS[TAG_CATEGORIES[2][0]] = '#eb0'
TAG_COLORS[TAG_CATEGORIES[3][0]] = '#4de94c'
TAG_COLORS[TAG_CATEGORIES[4][0]] = '#3783ff'
TAG_COLORS[TAG_CATEGORIES[5][0]] = '#4815aa'


class Author(models.Model):
    first_name = CharField('имя', max_length=20)
    second_name = CharField('отчество', max_length=30, blank=True)
    last_name = CharField('фамилия', max_length=30)
    title = FixedWidthTextField('титулы/регалии', max_length=500, blank=True)

    def __str__(self):
        text = '%s %s.' % (self.last_name, self.first_name[:1])
        if self.second_name:
            text += ' %s.' % self.second_name[:1]
        return text

    class Meta:
        verbose_name = 'автор'
        verbose_name_plural = 'авторы'
        ordering = ('last_name', 'first_name', 'second_name')


class TagGroup(models.Model):
    name = CharField('название', max_length=50)
    parent_tag = ForeignKey('Tag', verbose_name='родительская бирка',
                            help_text='Бирка, к которой относится группа.')
    def __str__(self):
        return '[%s] %s' % (self.parent_tag.name, self.name)

    class Meta:
        verbose_name = 'коллекция бирок'
        verbose_name_plural = 'коллекции бирок'


class Tag(models.Model):
    name = CharField('бирка', max_length=50)
    category = CharField('категрия', choices=TAG_CATEGORIES, max_length=1)
    groups = ManyToManyField(TagGroup, verbose_name='группа', blank=True)
    parent = ForeignKey('self', verbose_name='бирка-родитель', blank=True,
                        null=True)
    order = models.PositiveSmallIntegerField(
            'порядок', default=10, help_text='Порядок в рамках категории')

    def __str__(self):
        tag = self
        hierarchy = ['<strong>%s</strong>' % tag.name]
        while tag.parent:
            tag = tag.parent
            hierarchy.append(tag.name)
        hierarchy.reverse()
        hierarchy_text = ' &gt; '.join(tag_name for tag_name in hierarchy)
        text = '[%s] %s' % (self.get_category_display(), hierarchy_text)
        # NOTE: Двойные и одинарные кавычки далее принципиально важны, иначе
        # поломаются надписи в админковских фильтрах, так как этот текст
        # добавляется в частности внутрь атрибута title="".
        html = "<span style='font-weight: normal; color: %s'>%s</span>" % (
                TAG_COLORS[self.category], text)
        return mark_safe(html)

    class Meta:
        verbose_name = 'бирка'
        verbose_name_plural = 'бирки'
        ordering = ('category', 'order', 'id')



MARKDOWN_HELP = '''

    <p style="font-size: xx-small; margin-bottom: 1em">
    Для курсива, ссылок и абзацев используйте
    <a target="_blank" href="https://docs.google.com/document/d/1onDgE9wkZSGbXZg5V3GdoPx8gQ4fhXe73E7Sn0qvDY4">разметку Markdown</a>.</p>

'''
MARKDOWN2_HELP = '''

    <p style="font-size: xx-small; margin-bottom: 1em">
    Для курсива используйте
    <a target="_blank" href="https://docs.google.com/document/d/1onDgE9wkZSGbXZg5V3GdoPx8gQ4fhXe73E7Sn0qvDY4">разметку Markdown</a>.</p>

'''
MOSTLY_FOR_VIDEOS = '''

    Обязательно для видео, факультативно для книг и статей.<br>
    Ручное указание авторства в этом поле не приветствуется, так как<br>
    автор автоматически будет добавлен (если он выделен галочкой в поле<br>
    «Автор») при выводе заголовка аннотации на портале.

''' + MARKDOWN2_HELP
MOSTLY_FOR_TEXTS = '''

    Обязательно для книг и статей, факультативно для видео.

''' + MARKDOWN_HELP
FOR_TEXTS = 'Для книг и статей.' + MARKDOWN_HELP
FOR_VIDEOS = 'Для видео.' + MARKDOWN_HELP
ANCHOR_HELP = '''

    Якорь, чтобы сослаться на текущую аннотацию из другой аннотации.<br>
    Если ссылаться на данную аннотацию из другой нет необходимости,<br>
    то поле можно оставлять пустым.<br>
    <br>
    Если якорь аннотации на «ресурс N» задан так <span
    style="color: #070">ludogovsk8</span>, то сослаться<br>
    из текста другой аннотации на него можно так:
    <span style="color: #070">см. [ресурс N](#ludogovsk8)</span>.<br>

'''
YOUTUBE_ID_NAME = 'ID видео'
YOUTUBE_ID_HELP = '''

    Идентификатор видео на YouTube. Например, если ссылка на видео выглядит<br>
    так <i>https://www.youtube.com/watch?v=zDRRSVplgXM&t=10s</i>,
    то идентификтор<br>будет выглядеть вот так <i>zDRRSVplgXM</i>.

'''
URL_HELP = '''

    Указывать любые ссылки кроме ютьюбовских.<br>
    Ссылки на youtube указывать в поле «%s»<br>
    в виде идентификаторов видео.

''' % YOUTUBE_ID_NAME


def unwrap_html_p(text):
    if text.startswith('<p>'):
        text = text[3:]
    if text.endswith('</p>'):
        text = text[:-4]
    return text


class Annotation(models.Model):
    title = FixedWidthTextField('название', max_length=200, blank=True,
                                null=True, unique=True,
                                help_text=MOSTLY_FOR_VIDEOS)
    bib = FixedWidthTextField('библиографическая ссылка', max_length=2000,
                              blank=True, null=True, unique=True,
                              help_text=FOR_TEXTS)
    annotation = models.TextField('аннотация', blank=True, null=True,
                                  help_text=MOSTLY_FOR_TEXTS)
    teaser = models.TextField('тизер', blank=True, null=True,
                              help_text=FOR_VIDEOS)
    authors = ManyToManyField(Author, verbose_name='авторы', blank=True)
    tags = ManyToManyField(Tag, verbose_name='бирки')
    anchor = models.SlugField('якорь', max_length=30, blank=True, null=True,
                              help_text=ANCHOR_HELP, unique=True)
    # NOTE: Использовать для url стандартное джанговское поле URLField
    # нельзя, потому что оно не допускает относительных ссылок. А у нас
    # по крайней мере одна такая ссылка будет -- для самого нашего словаря.
    url = CharField('ссылка на ресурс', max_length=1000,
                    blank=True, null=True, unique=True, help_text=URL_HELP)
    youtube_id = CharField(YOUTUBE_ID_NAME, max_length=20, blank=True,
                           help_text=YOUTUBE_ID_HELP, null=True, unique=True)
    create_date = models.DateTimeField('время добавления', auto_now_add=True,
                                       blank=True)

    def get_title_html(self):
        title = self.title and self.title.strip()
        html = markdown.markdown(title) if title else ''
        return mark_safe(unwrap_html_p(html))

    def get_title_with_author_html(self):
        title = self.title and self.title.strip()
        text = title if title else ''
        if text:
            authors = list(self.authors.all())
            if authors:
                text2 = ', '.join('<i>%s</i>' % str(a) for a in authors)
                text = '%s %s' % (text2, text)
            text = markdown.markdown(text)
        return mark_safe(unwrap_html_p(text))

    def get_bib_html(self):
        bib = self.bib and self.bib.strip()
        html = markdown.markdown(bib) if bib else ''
        return mark_safe(html)

    def get_annotation_html(self):
        html = markdown.markdown(self.annotation) if self.annotation else ''
        return mark_safe(html)

    def get_teaser_html(self):
        html = markdown.markdown(self.teaser) if self.teaser else ''
        return mark_safe(html)

    def save(self, *args, **kwargs):
        for fieldname in ('title', 'bib', 'annotation', 'teaser',
                          'anchor', 'url', 'youtube_id'):
            value = getattr(self, fieldname)
            if not value or not value.strip():
                setattr(self, fieldname, None)
        super(Annotation, self).save(*args, **kwargs)

    def __str__(self):
        return self.title or self.bib

    class Meta:
        verbose_name = 'аннотация'
        verbose_name_plural = 'аннотации'
