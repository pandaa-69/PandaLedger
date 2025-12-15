from django.contrib import admin
from .models import Category , Expense 

admin.site.register(Category)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'category', 'date')
    
    list_filter = ('category', 'date')
    

