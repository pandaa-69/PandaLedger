from django.db import models
from django.conf import settings

class PortfolioSnapshot(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="snapshot")
    date = models.DateField()

    # the core numbers for the graph
    total_value = models.DecimalField(max_digits=15, decimal_places=2)
    invested_value = models.DecimalField(max_digits=15, decimal_places=2)

    # in future if i add AI analysis and benchmark comparison 
    benchmark_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date') #one per user per day 
        ordering = ['date']

    def __str__(self):
        return f"{self.user.username} - {self.date} - ₹{self.total_value}"
    