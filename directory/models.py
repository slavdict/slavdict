# -*- coding: UTF-8 -*-
from django.db import models

class Category(models.Model):

    slug = models.CharField(
        u'условное название',
        help_text = u'''Для использования при формировании
                        ручных запросов к БД, вроде «Выдай
                        мне все значения категории slug».''',
        max_length = 50,
        )

    description = models.CharField(
        u'описание',
        max_length = 50,
        )

    tag = models.CharField(
        u'ярлык по умолчанию',
        max_length = 50,
        )

    def __unicode__(self):
        return self.tag

    class Meta:
        verbose_name = u'категория'
        verbose_name_plural = u'категории'


class CategoryValue(models.Model):

    category = models.ForeignKey(
        Category,
        verbose_name = u'значение категории',
        )

    slug = models.CharField(
        u'условное название',
        help_text = u'''Для использования при формировании
                        ручных запросов к БД, вроде «Выдай
                        мне все возможные ярлыки для значения slug».''',
        max_length = 50,
        )

    tag = models.CharField(
        u'ярлык по умолчанию',
        max_length = 50,
        )

    order = models.PositiveSmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    pinned = models.BooleanField(
        u'закрепить',
        help_text = u'''Для возможности разбить все значения в данной категории
                        на часто используемые, которые необходимо выдать
                        группой в начале, и редкоиспользуемые, чтобы сделать,
                        например, для них ссылку «другое», при нажатии на
                        которую уже и будут они появляться для возможности выбора.''',
        )

    description = models.CharField(
        u'описание',
        max_length = 50,
        )

    # Данное поле первоначально придумано для указания CSS-класса,
    # потребовавшагося для отображении надписей на разных языках с
    # использованием разных шрифтов.
    css_class = models.CharField(
        u'CSS-класс',
        max_length = 50,
        blank = True,
        null = True,
        )

    # Данное поле первоначально придумано для указания 2-го CSS-класса,
    # потребовавшагося для отображении транслита некоторых языков.
    css_class2 = models.CharField(
        u'CSS-класс 2',
        max_length = 50,
        blank = True,
        null = True,
        )

    def __unicode__(self):
        return self.tag

    class Meta:
        verbose_name = u'значение категории'
        verbose_name_plural = u'значения категорий'
        ordering = ('category', 'order', 'id')


class TagLibrary(models.Model):

    slug = models.CharField(
        u'условное название',
        help_text = u'''Для использования при формировании
                        ручных запросов к БД, вроде «Выдай
                        мне все возможные ярлыки из библиотеки slug».''',
        max_length = 50,
        )

    description = models.TextField(
        u'Описание',
        help_text = u'''Описание целей/вариантов использования
                        данной библиотеки ярлыков.''',
        )

    def __unicode__(self):
        return self.slug

    class Meta:
        verbose_name = u'библиотека ярлыков'
        verbose_name_plural = u'библиотеки ярлыков'
        ordering = ('slug',)


class CategoryTag(models.Model):

    taglib = models.ForeignKey(
        TagLibrary,
        verbose_name = u'библиотека ярлыков',
        )

    category = models.ForeignKey(
        Category,
        verbose_name = u'категория',
        )

    tag = models.CharField(
        u'ярлык',
        max_length = 60,
        )

    def __unicode__(self):
        return self.tag

    class Meta:
        verbose_name = u'ярлык для категории'
        verbose_name_plural = u'ярлыки для категорий'


class ValueTag(models.Model):

    taglib = models.ForeignKey(
        TagLibrary,
        verbose_name = u'библиотека ярлыков',
        )

    catvalue = models.ForeignKey(
        CategoryValue,
        verbose_name = u'значение категории',
        )

    tag = models.CharField(
        u'ярлык',
        max_length = 50,
        )

    # Для возможности поменять порядок следования значений категории.
    # Если остается пустым, то порядок следования, как самих значений.
    order = models.SmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    pinned = models.BooleanField(
        u'закрепить',
        help_text = u'''Для возможности разбить все ярлыки в данной категории
                        значений на часто используемые, которые необходимо
                        выдать группой в начале, и редкоиспользуемые, чтобы
                        сделать, например, для них ссылку «другое», при нажатии
                        на которую уже и будут они появляться для возможности
                        выбора.''',
        )

    # Данное поле первоначально придумано для указания CSS-класса,
    # потребовавшагося для отображении надписей на разных языках с
    # использованием разных шрифтов.
    css_class = models.CharField(
        u'CSS-класс',
        max_length = 50,
        blank = True,
        null = True,
        )

    # Данное поле первоначально придумано для указания 2-го CSS-класса,
    # потребовавшагося для отображении транслита некоторых языков.
    css_class2 = models.CharField(
        u'CSS-класс 2',
        max_length = 50,
        blank = True,
        null = True,
        )


    def __unicode__(self):
        return self.tag

    class Meta:
        verbose_name = u'ярлык для значения'
        verbose_name_plural = u'ярлыки для значений'
        ordering = ('taglib', 'catvalue', 'catvalue__order')
