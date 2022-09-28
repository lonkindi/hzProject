from django.contrib import admin

from crm.models import Anket, TypeOperations


@admin.register(Anket)
class AnketAdmin(admin.ModelAdmin):
    list_display = ('date_filling', 'external_id', 'state',)
    list_editable = ('external_id', 'state',)


@admin.register(TypeOperations)
class TypeOperationsAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 's_name',)
    # list_editable = ('code', 'name', 's_name',)
