from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser #importing our Custom user table 

# Register  new CustomUser using the standard UserAdmin logic
admin.site.register(CustomUser, UserAdmin)


