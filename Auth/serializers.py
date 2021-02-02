from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'mobile', 'role']

    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("This email is already registered! Try with different one")
        return data



class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=10, min_length=3, required=True)
    password = serializers.CharField(max_length=20, min_length=6, required=True)

class ChangeUserPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=15, min_length=6)
    new_password = serializers.CharField(max_length=15, min_length=6)
    confirm_password = serializers.CharField(max_length=15, min_length=6)

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError("Password does not Match!")
        return data


class ForgotPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=6, max_length=16, required=True)
    confirm_password = serializers.CharField(min_length=6, max_length=16, required=True)

    def validate(self, data):
        if data.get('new_password') != data.get('confirm_password'):
            raise serializers.ValidationError("Password does not match!")
        return data