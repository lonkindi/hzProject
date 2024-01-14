from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple


from crm.models import TypeOperations, hzUserEvents, Candidate, MedCard, Doctor


class TypeOperationsInline(admin.StackedInline):
    model = TypeOperations
    extra = 3


@admin.register(MedCard)
class MedCardAdmin(admin.ModelAdmin):
    formfield_overrides = {models.ManyToManyField: {'widget': CheckboxSelectMultiple}, }
    list_display = ('date_filling', 'anket_id',)
    list_editable = ('anket_id',)


@admin.register(TypeOperations)
class TypeOperationsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 's_name', 'duration')
    list_display_links = ('code', 'name', 's_name',)
    list_editable = ('duration',)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    formfield_overrides = {models.ManyToManyField: {'widget': CheckboxSelectMultiple}, }
    search_fields = ['Sname', 'phoneNumber']
    date_hierarchy = 'date_oper'
    list_display = ('date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname', 'Doctor', 'Surgeon')
    list_display_links = ('date_oper', 'phoneNumber', 'Sname', 'Name', 'Mname')
    list_editable = ('Doctor',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('F_name', 'L_name', 'S_name', 'position', 'specialty')
    list_display_links = ('F_name', 'L_name', 'S_name', 'position', 'specialty',)
    # list_editable = ('plan_oper', 'opis_oper',)
