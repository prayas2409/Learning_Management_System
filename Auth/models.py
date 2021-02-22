from django.contrib.auth.base_user import BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class UserManager(BaseUserManager):

    def create_user(self, username, email, first_name, last_name, role, mobile, password):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, first_name=first_name, last_name=last_name, role=role,
                          mobile=mobile,
                          password=password)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, first_name, last_name, mobile, password):
        user = self.create_user(username=username, email=email, first_name=first_name, last_name=last_name,
                                mobile=mobile, role=Roles.user_role(),
                                password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        user.save()
        return user


class Roles(models.Model):
    role_id = models.IntegerField(default=False, blank=False, null=False, unique=True)
    role = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.role

    @staticmethod
    def user_role():
        admin_role = Roles.objects.filter(role='admin')
        if not admin_role:
            role = Roles(role_id=1, role='admin')
            role.save()
            return role
        return admin_role


class User(AbstractUser):
    """This is the base user model which is build extending the AbstractUser models functionalities.
    All the basic fields like username, first_name, last_name, email, password etc are extended in this model"""

    mobile = models.CharField(max_length=13)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['mobile', 'email', 'first_name', 'last_name']

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class TokenBlackList(models.Model):
    """This model is used to store the used token so that we could check is the token is already used or not"""

    token = models.CharField(max_length=300)
    time = models.DateTimeField(default=now)
