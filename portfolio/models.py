from django.db import models
from django.conf import settings
from decimal import Decimal

class Asset(models.Model):
    """
    Represents a financial instrument tracked by the system.
    Supports various asset types including Stocks, Mutual Funds, and Crypto.
    """
    ASSET_TYPES = [
        ('STOCK', 'Stock'),
        ('MF', 'Mutual Fund'),
        ('ETF', 'ETF'),
        ('CRYPTO', 'Crypto'),
        ('GOLD', 'Gold/Silver'),
        ('REIT', 'REIT'),
    ]
    CAP_CHOICES = [('LARGE', 'Large Cap'), ('MID', 'Mid Cap'), ('SMALL', 'Small Cap')]

    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=10, choices=ASSET_TYPES, default='STOCK')
    sector = models.CharField(max_length=50, blank=True, null=True)
    market_cap_category = models.CharField(max_length=10, choices=CAP_CHOICES, default='MID')
    last_price = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class Holding(models.Model):
    """
    Represents a user's ownership of a specific asset.
    Tracks the total quantity and the average buy price derived from transactions.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="holdings")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=15, decimal_places=4, default=0)
    avg_buy_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def current_value(self):
        """Calculate the current market value of the holding."""
        return round(float(self.quantity * self.asset.last_price), 2)

    def recalculate(self):
        """
        Recalculate the quantity and average buy price based on all transactions.
        If the total quantity drops to zero or less, the holding is removed.
        """
        txs = self.transactions.all()
        total_qty = Decimal(0)
        total_cost = Decimal(0)
        
        for tx in txs:
            if tx.type == 'BUY':
                total_cost += (tx.quantity * tx.price)
                total_qty += tx.quantity
            elif tx.type == 'SELL':
                total_qty -= tx.quantity
        
        # If Quantity is 0, delete the holding entirely to keep the portfolio clean.
        if total_qty <= 0:
            self.delete()
        else:
            self.avg_buy_price = total_cost / total_qty
            self.quantity = total_qty
            self.save()

    def __str__(self):
        return f"{self.user.username} - {self.asset.symbol}"

class Transaction(models.Model):
    """
    Represents a buy or sell action on a holding.
    Triggers a recalculation of the parent holding upon save.
    """
    TX_TYPES = [('BUY', 'Buy'), ('SELL', 'Sell')]
    holding = models.ForeignKey(Holding, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=4, choices=TX_TYPES)
    quantity = models.DecimalField(max_digits=15, decimal_places=4)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.holding.recalculate()