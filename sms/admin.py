from django.contrib import admin
from .models import SMSMessage


@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):

    list_display = (
        "message",
        "total_recipients",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "message",
    )

    ordering = (
        "-created_at",
    )

    list_per_page = 20