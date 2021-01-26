from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    mobile = models.CharField(max_length=13, default=None, null=True)
    role = models.CharField(choices=(('Mentor', 'Mentor'), ('Engineer', 'Engineer'), ('Admin', 'Admin')),
                            max_length=10)

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
