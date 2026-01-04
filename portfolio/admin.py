from django.contrib import admin
from .models import Asset, Holding, Transaction

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    """
    Configure the admin interface for Asset management.
    Includes filtering by type, sector, and market cap.
    """
    list_display = ('symbol', 'name', 'asset_type', 'sector', 'last_price', 'market_cap_category')
    search_fields = ('symbol', 'name')
    list_filter = ('asset_type', 'sector', 'market_cap_category')
    ordering = ('symbol',)

@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    """
    Configure the admin interface for User Holdings.
    Displays calculated current value and allows search by user/asset.
    """
    list_display = ('user', 'asset', 'quantity', 'avg_buy_price', 'current_value_display')
    search_fields = ('user__username', 'asset__symbol')
    list_filter = ('user',)

    def current_value_display(self, obj):
        return f"₹{obj.current_value()}"
    current_value_display.short_description = 'Current Value'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """
    Configure the admin interface for Transaction records.
    Includes a date hierarchy for timeline navigation.
    """
    list_display = ('holding', 'type', 'quantity', 'price', 'date')
    list_filter = ('type', 'date', 'holding__user')
    search_fields = ('holding__asset__symbol', 'holding__user__username')
    date_hierarchy = 'date'
    ordering = ('-date',)