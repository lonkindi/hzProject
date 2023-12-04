from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple


from crm.models import TypeOperations, hzUserEvents, Candidate, MedCard


class TypeOperationsInline(admin.StackedInline):
    model = TypeOperations
    extra = 3


@admin.register(MedCard)
class MedCardAdmin(admin.ModelAdmin):
    formfield_overrides = {models.ManyToManyField: {'widget': CheckboxSelectMultiple}, }
    list_display = ('date_filling', 'anket_id', 'state',)
    list_editable = ('anket_id', 'state',)


@admin.register(TypeOperations)
class TypeOperationsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 's_name', 'plan_oper', 'opis_oper')
    list_display_links = ('code', 'name', 's_name',)
    list_editable = ('plan_oper', 'opis_oper',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    formfield_overrides = {models.ManyToManyField: {'widget': CheckboxSelectMultiple}, }
    search_fields = ['Sname', 'phoneNumber']
    date_hierarchy = 'date_oper'
    list_display = ('date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname')
    list_display_links = ('date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname')
