from rest_framework import serializers
from .models import *
import sys

sys.path.append("..")
from Management.utils import Pattern


class RoleSerializer(serializers.ModelSerializer):
    """ This is the add role serializer"""
    class Meta:
        model = Roles
        fields = ['role_id', 'role']


class UserSerializer(serializers.ModelSerializer):
    """This Serializer is used to serialize user registration data
    """
    email = serializers.EmailField(required=True)
    first_name = serializers.RegexField(Pattern.NAME_PATTERN.value)
    last_name = serializers.RegexField(Pattern.NAME_PATTERN.value)
    mobile = serializers.RegexField(Pattern.MOBILE_PATTERN.value)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile', 'role']

    def validate(self, data):
        """If the mail id is already present in database then raising en exception
        """
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("This email is already registered! Try with different one")
        if User.objects.filter(mobile=data['mobile']).exists():
            raise serializers.ValidationError("This mobile number is already registered! Try with different one")
        return data


class UserLoginSerializer(serializers.ModelSerializer):
    """This Serializer is used to serializer user credential inputs
    """
    username = serializers.CharField(max_length=20, min_length=3, required=True)
    password = serializers.CharField(max_length=20, min_length=6, required=True)

    class Meta:
        model = User
        fields = ['username', 'password']
    # extra_kwargs = {'role':{'read_only':True}}


class ChangeUserPasswordSerializer(serializers.Serializer):
    """This serializer is used to serialize change password credential inputs"""

    old_password = serializers.CharField(max_length=20, min_length=6)
    new_password = serializers.CharField(max_length=20, min_length=6)
    confirm_password = serializers.CharField(max_length=20, min_length=6)

    def validate(self, data):
        """If new password and confirm password are not matching then raising an exception"""

        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError("Password does not Match!")
        return data


class ForgotPasswordSerializer(serializers.ModelSerializer):
    """This serializer is used to serialize forgot password input as well as new login link with token api's input.
       Input Field: email field
    """

    class Meta:
        model = User
        fields = ['email']


class ResetPasswordSerializer(serializers.Serializer):
    """This serializer is used to serialize reset password API's inputs as well as Change Password on First Access API's
    inputs.
    """
    new_password = serializers.CharField(min_length=6, max_length=20, required=True)
    confirm_password = serializers.CharField(min_length=6, max_length=20, required=True)

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError("Password does not match!")
        return data
