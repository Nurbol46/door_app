from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('user', 'User'),
    )
    full_name = models.CharField(max_length=150)
    number = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.full_name
    
class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='shops')
    name = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    street = models.CharField(max_length=150)
    house_number = models.CharField(max_length=20)


    def __str__(self):
        return self.name
