from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple


from crm.models import Anket, TypeOperations, hzUserEvents, Candidate


class TypeOperationsInline(admin.StackedInline):
    model = TypeOperations
    extra = 3


@admin.register(Anket)
class AnketAdmin(admin.ModelAdmin):
    list_display = ('date_filling', 'external_id', 'state',)
    list_editable = ('external_id', 'state',)


@admin.register(TypeOperations)
class TypeOperationsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 's_name',)
    list_display_links = ('code', 'name', 's_name',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    formfield_overrides = {models.ManyToManyField: {'widget': CheckboxSelectMultiple}, }
    date_hierarchy = 'date_oper'
    list_display = ('date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname')
    list_display_links = ('date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname')
