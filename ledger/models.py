from django.db import models
from django.conf import settings

class Category(models.Model):
    """
    Represents an expense category (e.g., 'Groceries', 'Rent').
    Categories are user-specific to allow for personalized organization.
    """
    name = models.CharField(max_length=50, help_text="Name of the category")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='categories',
        help_text="The user who owns this category"
    )

    class Meta:
        verbose_name_plural = "Categories" 
        unique_together = ("name", "user")

    def __str__(self):
        return self.name

class Expense(models.Model):
    """
    Records an individual financial transaction (outflow).
    Linked to a user and optionally a category.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    # If a category is deleted, keep the expense but mark as Uncategorized (NULL)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='expenses',
        help_text="Category of the expense (optional)"
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Expense amount")
    description = models.CharField(max_length=255, help_text="Short description of the expense")
    date = models.DateField(help_text="Date and time of the expense")

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
        ]
    
    def __str__(self):
        cat_name = self.category.name if self.category else "Uncategorized"
        return f"{self.description} - {self.amount} ({cat_name})"
