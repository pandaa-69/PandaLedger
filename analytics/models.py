from django.db import models
from django.conf import settings

class PortfolioSnapshot(models.Model):
    """
    Captures the daily state of a user's portfolio for historical analysis.

    This model stores the total value and invested value at the end of each day,
    allowing for performance tracking and graphing over time.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="snapshots")
    date = models.DateField(help_text="The date of the snapshot recording")

    # Core metrics
    total_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total current market value of the portfolio")
    invested_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Total capital invested")

    # Future-proofing for advanced analytics
    benchmark_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Optional: Value of a benchmark index (e.g., Nifty 50) for comparison"
    )

    class Meta:
        unique_together = ('user', 'date') # Ensure only one snapshot per user per day
        ordering = ['date'] # Chronological order for easier graphing

    def __str__(self):
        return f"{self.user.username} | {self.date} | ₹{self.total_value}"

    @property
    def profit_loss(self):
        """Calculates the absolute profit or loss."""
        return self.total_value - self.invested_value

    @property
    def profit_loss_percentage(self):
        """Calculates the percentage profit or loss."""
        if self.invested_value == 0:
            return 0
        return round(((self.total_value - self.invested_value) / self.invested_value) * 100, 2)
