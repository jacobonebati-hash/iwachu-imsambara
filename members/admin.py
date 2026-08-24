from django.contrib import admin
from .models import Member, SMSMessage


admin.site.register(Member)
admin.site.register(SMSMessage)