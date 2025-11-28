# assets/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Extra", {"fields": ("role", "base")}),
    )

admin.site.register(Base)
admin.site.register(Asset)
admin.site.register(Purchase)
admin.site.register(Transfer)
admin.site.register(Assignment)
admin.site.register(Log)
