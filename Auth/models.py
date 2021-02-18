from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now
from .permissions import Role

class User(AbstractUser):
    """This is the base user model which is build extending the AbstractUser models functionalities.
    All the bassic fields like username, first_name, last_name, email, password etc are extended in this model"""

    def get_roles():
        roles = [Role.ADMIN.value, Role.MENTOR.value, Role.STUDENT.value]
        return ((role, role) for role in roles)      

    mobile = models.CharField(max_length=13)
    role = models.CharField(choices= get_roles(), max_length=255, default="AnonymousUser")

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class TokenBlackList(models.Model):
    """This model is used to store the used token so that we could check is the token is already used or not"""
    
    token = models.CharField(max_length=300)
    time = models.DateTimeField(default=now)