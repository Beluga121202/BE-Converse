from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_deactivated = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=12, default='0123456789')
    address = models.CharField(max_length=255, default='TPHCM')
