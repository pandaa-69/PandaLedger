from django.contrib import admin
from .models import MarketCache

@admin.register(MarketCache)
class MarketCacheAdmin(admin.ModelAdmin):
    list_display = ('id', 'last_updated')