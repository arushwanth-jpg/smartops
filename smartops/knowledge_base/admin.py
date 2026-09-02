# Register your models here.
from django.contrib import admin

from .models import (
    KBArticle,
    KBArticleVersion,
    TicketKBLink,
)


@admin.register(KBArticle)
class KBArticleAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "title",
        "status",
        "category",
        "created_by",
        "updated_at",
    ]

    list_filter = [
        "status",
        "category",
    ]

    search_fields = [
        "title",
        "content",
        "summary",
    ]

    prepopulated_fields = {
        "slug": ("title",)
    }


@admin.register(KBArticleVersion)
class KBArticleVersionAdmin(admin.ModelAdmin):

    list_display = [
        "article",
        "version_number",
        "changed_by",
        "created_at",
    ]

    search_fields = [
        "article__title",
    ]


@admin.register(TicketKBLink)
class TicketKBLinkAdmin(admin.ModelAdmin):

    list_display = [
        "ticket",
        "article",
        "linked_by",
        "created_at",
    ]
