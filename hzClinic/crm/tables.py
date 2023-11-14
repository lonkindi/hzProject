import django_tables2 as tables
from crm.models import Candidate


class CandidateTable(tables.Table):
    phoneNumber = tables.Column(verbose_name='Номер телефона',
                          order_by=('phoneNumber', '-phoneNumber'))
    date_oper = tables.DateColumn(verbose_name='Дата операции',
                           order_by=('date_oper', '-date_oper'))
    Sname = tables.Column(verbose_name='Фамилия',
                                     order_by=('Sname',
                                               '-Sname'))
    Name = tables.Column(verbose_name='Имя',
                          order_by=('Name',
                                    '-Name'))
    Mname = tables.Column(verbose_name='Отчество',
                          order_by=('Mname',
                                    '-Mname'))
    typeOpers = tables.ManyToManyColumn(verbose_name='Запланированные операции',
                              order_by=('typeOpers', '-typeOpers'))
    notes = tables.Column(verbose_name='Примечания',
                                order_by=('notes', '-notes'))

    class Meta:
        model = Candidate
        template_name = "django_tables2/bootstrap5.html"
