# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, UserManager

class CustomUser(User):
    """Модель Пользователя, основанная на стандартной
    для Django модели User, но с дополнительными полями."""

    second_name = models.CharField(
        u'отчество',
        max_length=30,
        blank = True,
        )
#
#    dict_roles = models.ManyToManyField(
#        'slavdict_roles.models.Role',
#        verbose_name = u'роль в работе над словарём'
#        )

    # Используем UserManager, чтобы иметь в наличии
    # стандартный метод менеджера модели User, а именно
    # create_user и т.п.
    objects = UserManager()

    # принадлежит ли пользователь к одной из привиллегированных
    # групп пользователей (является суперпользователем,
    # администратором или редактором [в отл. от авторов])
    @property
    def is_admeditor(self):
        user_groups = [i[0] for i in self.groups.values_list('name')]
        return self.is_superuser or 'editors' in user_groups or 'admins' in user_groups

    @property
    def is_editor(self):
        user_groups = [i[0] for i in self.groups.values_list('name')]
        return 'editors' in user_groups

    @property
    def is_hellinist(self):
        user_groups = [i[0] for i in self.groups.values_list('name')]
        return 'hellinists' in user_groups

    def __unicode__(self):
        try:
            first_name_initial = u' %s.' % self.first_name[0]
            try:
                second_name_initial = u'%s.' % self.second_name[0]
            except IndexError:
                second_name_initial = u''
        except IndexError:
            first_name_initial = u''
            second_name_initial = u''
        return u'%s%s%s' % (
            self.last_name,
            first_name_initial,
            second_name_initial,
            )

    class Meta:
        verbose_name = u'пользователь'
        verbose_name_plural = u'пользователи'
        ordering = ('last_name', 'first_name')
