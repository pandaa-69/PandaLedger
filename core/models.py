from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    # we are inheriting all the standard fields like  username , password, email 
    # we can add extra field later as we require like phone_num 

    # new field for montthly budget limit set by the user for the spending 
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=20000.0)
    # risk appetite 
    risk_appetite =models.CharField( max_length=20,
    choices=[('LOW', 'Conservative'), ('MID', 'Moderate'), ('HIGH', "Agrressive")],
    default='MID'                                            
    )

    def __str__(self):
        return self.username