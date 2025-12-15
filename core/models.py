from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    # we are inheriting all the standard fields like  username , password, email 
    # we can add extra field later as we require like phone_num 
    pass

    def __str__(self):
        return self.username