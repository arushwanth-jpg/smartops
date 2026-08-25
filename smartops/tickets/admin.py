from django.contrib import admin

from .models import Attachment,Category,Comment,Tag,Ticket,TicketEvent


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "status",
        "priority",
        "requester",
        "assigned_agent",
        "created_at",
    )

    list_filter = (
        "status",
        "priority",
        "category",
    )

    search_fields = (
        "title",
        "description",
        "requester__username",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "author",
        "comment_type",
        "created_at",
    )


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "uploaded_by",
        "original_filename",
        "uploaded_at",
    )


@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "ticket",
        "actor",
        "action",
        "created_at",
    )

    readonly_fields = (
        "ticket",
        "actor",
        "action",
        "old_value",
        "new_value",
        "created_at",
    )