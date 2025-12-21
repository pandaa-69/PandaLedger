from django.contrib import admin
from .models import PortfolioSnapshot

@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'total_value', 'invested_value')
    list_filter = ('user', 'date')
    date_hierarchy = 'date'  # Adds a nice date navigation bar
    ordering = ('-date',)    # Shows newest first