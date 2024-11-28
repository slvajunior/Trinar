from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Configurar campos adicionais no admin
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_name',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('full_name',)}),
    )
