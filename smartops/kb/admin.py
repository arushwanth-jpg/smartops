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
        "author",
        "created_at",
        "published_at",
    ]

    search_fields = [
        "title",
        "content",
    ]

    list_filter = [
        "status",
        "created_at",
    ]

    prepopulated_fields = {
        "slug": ("title",)
    }


@admin.register(KBArticleVersion)
class KBArticleVersionAdmin(admin.ModelAdmin):

    list_display = [
        "article",
        "version_number",
        "created_by",
        "created_at",
    ]


@admin.register(TicketKBLink)
class TicketKBLinkAdmin(admin.ModelAdmin):

    list_display = [
        "ticket",
        "article",
        "linked_by",
        "created_at",
    ]