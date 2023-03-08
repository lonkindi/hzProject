import datetime

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from users.models import CustomUser


class hzUserInfo(models.Model):
    class UserTypeChoices(models.TextChoices):
        admin = 'admin', _('Администратор'),
        doctor = 'doctor', _('Врач'),
        patient = 'patient', _('Пациент')

    hz_user = models.OneToOneField(CustomUser, verbose_name='Пользователь',
                                   blank=True, null=True,
                                   on_delete=models.CASCADE)
    f_name = models.CharField(max_length=30, verbose_name='Фамилия', blank=True)
    l_name = models.CharField(max_length=30, verbose_name='Имя', blank=True)
    S_name = models.CharField(max_length=30, verbose_name='Отчество', blank=True)
    DOB = models.DateField(verbose_name='Дата рождения')
    reg_address = models.CharField(max_length=255, verbose_name='Адрес регистрации', blank=True)
    phone_number = models.CharField(max_length=12, verbose_name='Телефон', blank=True)
    type = models.CharField(verbose_name='Тип пользователя', choices=UserTypeChoices.choices, max_length=7,
                            default='patient')
    foto = models.FileField(verbose_name='Фотография',
                            upload_to=f'crm/foto/users/%Y/%m/%d/',
                            # upload_to=f'crm/media/foto/users/%Y/%m/%d/',

                            blank=True, null=True)

    class Meta:
        verbose_name = 'Информация о пользователе'
        verbose_name_plural = 'Информация пользователей'
        # ordering = ('+f_name')

    def __str__(self):
        return self.f_name


class hzUserEvents(models.Model):
    hz_user = models.ForeignKey(CustomUser, verbose_name='Пользователь', related_name='events',
                                blank=True, null=True,
                                on_delete=models.CASCADE)
    date_time = models.DateTimeField(verbose_name='Дата и время', default=datetime.datetime.today)
    title = models.CharField(max_length=100, verbose_name='Событие')
    description = models.TextField(verbose_name='Описание')
    media = models.FileField(verbose_name='Медиафайлы', name='event_media',
                             upload_to=f'CRM/static/CRM/upload/events/',
                             blank=True, null=True)

    class Meta:
        verbose_name = 'Заметка'
        verbose_name_plural = "Список событий"

        ordering = ('-date_time',)

    def __str__(self):
        return self.title


class Anket(models.Model):
    """
    Модель анкеты
    """
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    state = models.PositiveIntegerField(verbose_name='Статус')
    content = models.JSONField(verbose_name='Содержимое анкеты')
    date_filling = models.DateField(verbose_name='Дата заполнения', default=datetime.datetime.today)

    class Meta:
        verbose_name = 'Анкета'
        verbose_name_plural = "Анкеты"
        ordering = ('-external_id',)

    def __str__(self):
        return str(self.external_id)


class TypeOperations(models.Model):
    """
    Модель видов операций
    """
    code = models.PositiveIntegerField(verbose_name='Код операции')
    name = models.CharField(max_length=50, verbose_name='Название операции')
    s_name = models.CharField(max_length=25, verbose_name='Сокращённое название')
    zaloby = models.TextField(max_length=255, null=True, blank=True, verbose_name='Жалобы')
    pri_osmotre = models.TextField(max_length=255, null=True, blank=True, verbose_name='При осмотре')
    osn_zabol = models.TextField(max_length=255, null=True, blank=True, verbose_name='Основное заболевание')
    MKB = models.CharField(max_length=20, null=True, blank=True, verbose_name='Код МКБ')
    plan_lech = models.TextField(max_length=255, null=True, blank=True, verbose_name='План лечения')
    obosnov = models.TextField(max_length=255, null=True, blank=True, verbose_name='Обоснование')
    # PZK = models.CharField(max_length=20, null=True, blank=True, verbose_name='Подкожно-жировая клетчатка')
    naimen_oper = models.CharField(max_length=100, null=True, blank=True, verbose_name='Наименование операции')
    kod_usl = models.CharField(max_length=20, null=True, blank=True, verbose_name='Код услуги')
    plan_oper = models.TextField(max_length=255, null=True, blank=True, verbose_name='План операции')
    opis_oper = models.TextField(max_length=2048, null=True, blank=True, verbose_name='Описание операции')
    kol_instr = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Кол-во инструментов')
    kol_salf = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Кол-во салфеток')
    krovop = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Кровопотеря')
    naznach = models.TextField(max_length=255, null=True, blank=True, verbose_name='Назначения')
    primen_lec = models.TextField(max_length=255, null=True, blank=True, verbose_name='Применение лекарств')
    rezult = models.TextField(max_length=255, null=True, blank=True, verbose_name='Результат')
    srok_gosp = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Срок госпитализации')

    class Meta:
        verbose_name = 'Вид операции'
        verbose_name_plural = "Виды операций"
        ordering = ('code',)

    def __str__(self):
        return str(self.name)


class Candidate(models.Model):
    """
    Модель кандидата на операцию
    """
    phoneNumberRegex = RegexValidator(regex=r"^\+?1?\d{8,15}$", message='Неверный формат ввода номера телефона!')
    phoneNumber = models.CharField(validators=[phoneNumberRegex], max_length=16, unique=False,
                                   verbose_name='Номер телефона (phoneNumber)')
    date_oper = models.DateField(verbose_name='Дата операции (date_oper)', default=datetime.date.today)
    Sname = models.CharField(max_length=25, verbose_name='Фамилия (Sname)')
    Name  = models.CharField(max_length=25, verbose_name='Имя (Name)')
    Mname = models.CharField(max_length=25, verbose_name='Отчество (Mname)', blank=True)
    typeOpers = models.ManyToManyField(TypeOperations, verbose_name='Операции (typeOpers)', related_name='operations')



    class Meta:
        verbose_name = 'Кандидат'
        verbose_name_plural = "Кандидаты"
        ordering = ('date_oper',)

    def __str__(self):
        return str(self.date_oper) + '-' + self.Sname + ' ' + self.Name + ' ' + self.Mname

