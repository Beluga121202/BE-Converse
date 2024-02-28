from django.db import models
from django.contrib.auth.models import AbstractUser
from birthday import BirthdayField, BirthdayManager

# Create your models here.
GENDER_CHOICES = (
    (0, 'male'),
    (1, 'female'),
    (2, 'not specified'),
)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)
    is_deactivated = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=12, default='0123456789')
    address = models.CharField(max_length=255, default='TPHCM')
    gender = models.IntegerField(choices=GENDER_CHOICES, default=0)
    birthday = BirthdayField(default='2002-12-12', blank=True)


class Product(models.Model):
    product_type = models.CharField(max_length=255, default='')
    product_id = models.CharField(max_length=255, default='', unique=True)
    product_name = models.CharField(max_length=255, default='')
    img = models.ImageField(upload_to='images/', blank=True, null=True)
    quantity = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)
    place = models.CharField(max_length=255, default='')
    product_line = models.CharField(max_length=255, default='')
