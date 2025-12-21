from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Add our new fields to the "Personal info" section in Admin
    fieldsets = UserAdmin.fieldsets + (
        ('Financial Profile', {'fields': ('monthly_budget', 'risk_appetite')}),
    )
    list_display = ('username', 'email', 'monthly_budget', 'risk_appetite', 'is_staff')

admin.site.register(CustomUser, CustomUserAdmin)