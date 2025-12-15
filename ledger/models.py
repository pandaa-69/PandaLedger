from django.db import models
from django.conf import settings #this will import our custom user 

class Category(models.Model):
    name = models.CharField(max_length=50)

    # link so that one user can have many categories

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "Categories" # doing this to fix the typo in the admin pannel
        unique_together = ("name", "user")


    def __str__(self):
        return f"{self.name}"
    
class Expense(models.Model):
    # linking the user 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # linking the category to know what type of expense also in such a way that if we delete that specific category expense still exist in the DB and and financial history is not lost 
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateTimeField()

    class Meta:
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["user", "date"]),
            models.Index(fields=["user", "category"]),
        ]
    
    def __str__(self):
        return f"{self.description} - {self.amount} Category: {self.category}"