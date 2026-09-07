from django.contrib import admin

from .models import ConfirmationToken, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_confirmed", "is_locked")


@admin.register(ConfirmationToken)
class ConfirmationTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "expires_at", "attempts")
