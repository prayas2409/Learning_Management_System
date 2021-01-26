from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    mobile = models.CharField(max_length=13, default=None, null=True)
    role = models.CharField(choices=((1, 'Mentor'), (2, 'Engineer'), (3, 'Admin')), max_length=10)

