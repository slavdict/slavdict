from django.db import models
from django.contrib.auth.models import User, UserManager

class CustomUser(User):
    """Модель Пользователя, основанная на стандартной
    для Django модели User, но с дополнительными полями."""

    second_name = models.CharField(
        'отчество',
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

    # Различение пользователей,
    # занимающихся подготовкой тома к печати (True), и остальных (False).
    @property
    def has_key_for_preplock(self):
        l = ('\u0434\u043e\u0431\u0440\u043e\u0432',
             '\u0445\u0438\u0442\u0440')
        return self.last_name.lower().startswith(l)

    # принадлежит ли пользователь к одной из привиллегированных групп (является
    # суперпользователем, администратором или редактором [в отл. от авторов])
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

    def __str__(self):
        try:
            first_name_initial = ' %s.' % self.first_name[0]
            try:
                second_name_initial = '%s.' % self.second_name[0]
            except IndexError:
                second_name_initial = ''
        except IndexError:
            first_name_initial = ''
            second_name_initial = ''
        return '%s%s%s' % (
            self.last_name,
            first_name_initial,
            second_name_initial,
            )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('last_name', 'first_name')
