from django.contrib import admin

from .models import DepartmentGroup


@admin.register(DepartmentGroup)
class DepartmentGroupAdmin(admin.ModelAdmin):
    list_display = ("name",)
