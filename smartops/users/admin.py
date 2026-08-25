from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Team


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "role",
        "team",
        "is_active",
    )

    list_filter = (
        "role",
        "team",
        "is_active",
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "created_at",
    )