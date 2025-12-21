from django.db import models

class MarketCache(models.Model):
    """
    Stores the entire market dashboard JSON blob.
    We only need 1 row in this table ever.
    """
    data = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Market Data (Updated: {self.last_updated})"