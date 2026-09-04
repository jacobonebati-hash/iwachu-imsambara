from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):

    list_display = (
        "jina",
        "simu",
        "kitongoji",
        "jinsia",
        "tarehe_ya_usajili",
        "status",
    )

    list_filter = (
        "status",
        "jinsia",
        "kitongoji",
    )

    search_fields = (
        "jina",
        "simu",
        "kitongoji",
    )

    ordering = (
        "-tarehe_ya_usajili",
    )

    list_per_page = 20