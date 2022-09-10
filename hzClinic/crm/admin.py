from django.contrib import admin

from crm.models import Anket


@admin.register(Anket)
class AnketAdmin(admin.ModelAdmin):
    list_display = ('date_filling', 'external_id', 'state',)
    list_editable = ('external_id', 'state',)

