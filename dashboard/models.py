from django.db import models

class MarketCache(models.Model):
    """
    Stores a cached snapshot of the market dashboard data.
    
    This model acts as a persistent layout cache to ensure that even if external APIs
    fail or the cache is cleared, the dashboard can serve the last known good state.
    Designed to hold a singleton record (id=1).
    """
    data = models.JSONField(
        default=dict,
        help_text="The full JSON blob containing market summary, indices, and news."
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of when this snapshot was last refreshed."
    )

    def __str__(self):
        return f"Market Data Snapshot (Updated: {self.last_updated})"
