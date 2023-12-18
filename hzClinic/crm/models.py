import datetime

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
    # LTR = models.TextField(max_length=2048, null=True, blank=True, verbose_name='Лечебные и трудовые рекомендации ')
    # duration = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Продолжительнсть')


    class Meta:
        verbose_name = 'Вид операции'
        verbose_name_plural = "Виды операций"
        ordering = ('code',)

    def __str__(self):
        return str(self.name)


class MedCard(models.Model):
    """
    Модель Медкарты
    """
    PZK_Choices = (('нормотрофическая', 'нормотрофическая'), ('гипертрофическая', 'гипертрофическая'))
    schema_Choices = (('голова', 'голова'), ('тело', 'тело'), ('голова + тело', 'голова + тело'))
    anest_Choices = (('общая ингаляционная анестезия', 'общая ингаляционная анестезия'),
                     ('общая ингаляционная анестезия + ИВЛ', 'общая ингаляционная анестезия + ИВЛ'),
                     ('местная анестезия', 'местная анестезия'),
                     ('местная анестезия + мониторинг', 'местная анестезия + мониторинг'))
    gk_Choices = (('О(I)', 'О(I)'), ('A(II)', 'A(II)'), ('B(III)', 'B(III)'), ('AB(IV)', 'AB(IV)'))
    rh_Choices = (('+', '+'), ('-', '-'))
    kell_Choices = (('отрицательный', 'отрицательный'), ('положительный', 'положительный'))

    anket_id = models.PositiveIntegerField(verbose_name='№ анкеты')
    phone = models.CharField(max_length=16, verbose_name='Номер телефона')
    date_filling = models.DateField(verbose_name='Дата заполнения', default=datetime.datetime.today)
    date_oper = models.DateField(verbose_name='Дата операции', default=datetime.datetime.today)

    s_name = models.CharField(max_length=25, verbose_name='Фамилия')
    name = models.CharField(max_length=25, verbose_name='Имя')
    m_name = models.CharField(max_length=25, verbose_name='Отчество', blank=True)
    DateOfB = models.DateField(verbose_name='Дата рождения')
    AddressRow = models.CharField(max_length=255, verbose_name='Адрес места жительства из анкеты')
    Address = models.CharField(max_length=255, verbose_name='Адрес обработанный (будет использован в документах)')
    veSub = models.CharField(max_length=100, verbose_name='Субъект (Республика/Край/Область)')
    veRn = models.CharField(max_length=100, verbose_name='Район субъекта')
    veGor = models.CharField(max_length=100, verbose_name='Город')
    veNP = models.CharField(max_length=100, verbose_name='Населённый пункт')
    veUl = models.CharField(max_length=100, verbose_name='Улица (без ул.)')
    veDom = models.CharField(max_length=100, verbose_name='Номер дома')
    veStr = models.CharField(max_length=100, verbose_name='Строение/Корпус/Владение и т.д.')
    veKv = models.CharField(max_length=100, verbose_name='Квартира')
    PerZ = models.CharField(max_length=100, verbose_name='Перенесённые и хронические заболевания?')
    PerO = models.CharField(max_length=100, verbose_name='Перенесённые пластические операции')
    PerT = models.CharField(max_length=100, verbose_name='Перенесённые травмы')
    PerG = models.CharField(max_length=100, verbose_name='Перенесённые гемотрансфузии')
    Allerg = models.CharField(max_length=100, verbose_name='Аллергии')
    VICH = models.CharField(max_length=100, verbose_name='ВИЧ')
    Gepatit = models.CharField(max_length=100, verbose_name='Гепатит')
    Tub = models.CharField(max_length=100, verbose_name='Туберкулёз')
    Diabet = models.CharField(max_length=100, verbose_name='Диабет')
    Vener = models.CharField(max_length=100, verbose_name='Венерические заболевания')
    Alk = models.CharField(max_length=100, verbose_name='Отношение к алкоголю')
    Kur = models.CharField(max_length=100, verbose_name='Отношение к курению')
    Nark = models.CharField(max_length=100, verbose_name='Отношение к наркотикам')
    MedPrep = models.CharField(max_length=100, verbose_name='Лекарственные препараты на постоянной основе')
    MedIzd = models.CharField(max_length=100, verbose_name='Медицинские изделия')
    Gender = models.CharField(max_length=100, verbose_name='Пол')
    oGender = models.CharField(max_length=100, verbose_name='Дополнительная информация для осмотра, в зависимости от пола')
    Rost = models.CharField(max_length=100, verbose_name='Рост, см')
    Massa = models.CharField(max_length=100, verbose_name='Вес, кг')
    GK = models.CharField(max_length=100, choices=gk_Choices, verbose_name='Группа крови (O(I), A(II), B(III), AB(IV))')
    RH = models.CharField(max_length=100, choices=rh_Choices, verbose_name='Резус-фактор (+, -)')
    KELL = models.CharField(max_length=100, choices=kell_Choices, default=1,
                            verbose_name='Келл-фактор (отрицательный, положительный)')
    typeOpers = models.ManyToManyField(TypeOperations, verbose_name='Операции (typeOpers)',
                                       related_name='medcard_operations')
    PZK = models.CharField(max_length=100, choices=PZK_Choices, verbose_name='Состояние ПЖК')
    anest = models.CharField(max_length=100, choices=anest_Choices, verbose_name='Анестезия')
    schema = models.CharField(max_length=100, choices=schema_Choices, verbose_name='Схема к протоколу')

    class Meta:
        verbose_name = 'Медкарта'
        verbose_name_plural = "Медкарты"
        ordering = ('-date_oper',)

    def __str__(self):
        return str(self.anket_id)




class Candidate(models.Model):
    """
    Модель кандидата на операцию
    """
    class SurgeonChoices(models.TextChoices):
        KhotyanAR = 'Хотян А.Р.', _('Хотян А.Р.'),
        MamedovGT = 'Мамедов Г.Т.', _('Мамедов Г.Т.')

    phoneNumber = models.CharField(max_length=16, unique=False, verbose_name='Номер телефона (phoneNumber)')
    date_oper = models.DateField(verbose_name='Дата операции (date_oper)', default=datetime.date.today)
    Sname = models.CharField(max_length=25, verbose_name='Фамилия (Sname)')
    Name = models.CharField(max_length=25, verbose_name='Имя (Name)')
    Mname = models.CharField(max_length=25, verbose_name='Отчество (Mname)', blank=True)
    typeOpers = models.ManyToManyField(TypeOperations, verbose_name='Операции (typeOpers)',
                                       related_name='candidate_operations')
    Surgeon = models.CharField(verbose_name='Хирург', choices=SurgeonChoices.choices, max_length=15,
                               default='Хотян А.Р.')
    notes = models.TextField(max_length=255, verbose_name='Примечания (notes)', blank=True)

    class Meta:
        verbose_name = 'Кандидат'
        verbose_name_plural = "Кандидаты"
        ordering = ('date_oper',)

    def __str__(self):
        return str(self.date_oper) + '-' + self.Sname + ' ' + self.Name + ' ' + self.Mname



