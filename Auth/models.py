from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class User(AbstractUser):
    """This is the base user model which is build extending the AbstractUser models functionalities.
    All the bassic fields like username, first_name, last_name, email, password etc are extended in this model"""

    mobile = models.CharField(max_length=13, unique=True)
    role = models.CharField(choices=(('Mentor', 'Mentor'), ('Engineer', 'Engineer'), ('Admin', 'Admin')),
                            max_length=10)
    is_first_time_login = models.BooleanField(default=True)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class TokenBlackList(models.Model):
    """This model is used to store the used token so that we could check is the token is already used or not"""
    
    token = models.CharField(max_length=300)
    time = models.DateTimeField(default=now)