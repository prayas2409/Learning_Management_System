from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class User(AbstractUser):
    mobile = models.CharField(max_length=13, unique=True)
    role = models.CharField(choices=(('Mentor', 'Mentor'), ('Engineer', 'Engineer'), ('Admin', 'Admin')),
                            max_length=10)
    is_first_time_login = models.BooleanField(default=True)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class TokenBlackList(models.Model):
    token = models.CharField(max_length=300)
    time = models.DateTimeField(default=now)