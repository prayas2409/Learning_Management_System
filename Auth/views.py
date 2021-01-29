from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from .serializers import UserSerializer, UserLoginSerializer, ChangeUserPasswordSerializer, \
    ForgotPasswordSerializer, ResetPasswordSerializer
from .permissions import isAdmin
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from .JWTAuthentication import JWTAuth
from django.utils.decorators import method_decorator
from .middlewares import SessionAuthentication
from django.contrib.auth.hashers import check_password
from .models import User
import sys

sys.path.append('..')
from LMS.mailConfirmation import Email


@method_decorator(SessionAuthentication, name='dispatch')
class UserRegistrationView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (isAdmin,)

    def post(self, request):
        """This API is used to Add user like Mentor,Engineer or another Admin to the system by an Admin
         and informs the user about their account creation via email
         request parms : user related data like username, name, email etc
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data = {
            'name': f"{request.data['first_name']} {request.data['last_name']}",
            'username': request.data['username'],
            'password': request.data['password'],
            'role': request.data['role'],
            'email': request.data['email'],
            'site': get_current_site(request).domain
        }
        Email.sendEmail(Email.configureAddUserEmail(data))
        return Response({'response': f"A new {request.data['role']} is added"}, status=status.HTTP_201_CREATED)


class UserLoginView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        password = serializer.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            request.session[username] = JWTAuth.getToken(username=username, password=password)
            return Response({'response': 'You are logged in'}, status=status.HTTP_200_OK)
        return Response({'response': 'Bad credential found'}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(SessionAuthentication, name='dispatch')
class UserLogoutView(GenericAPIView):
    def delete(self, request):
        """This API is used to log user out and to clear the user session
        """
        request.session.pop(request.user.username)
        logout(request)
        return Response({'response': 'You are logged out'}, status=status.HTTP_204_NO_CONTENT)


@method_decorator(SessionAuthentication, name='dispatch')
class ChangeUserPasswordView(GenericAPIView):
    serializer_class = ChangeUserPasswordSerializer

    def put(self, request):
        """This API is used to change user password
        @request_parms = old password, new password and confirm password
        @rtype: saves new password in database
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.data.get('old_password')
        if check_password(old_password, request.user.password):
            request.user.set_password(raw_password=serializer.data.get('new_password'))
            request.user.save()
            return Response({'response': 'Your password is changed successfully!'}, status=status.HTTP_200_OK)
        return Response({'response': 'Old password does not match!'}, status=status.HTTP_401_UNAUTHORIZED)


class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        """This API is used to send reset password link to user email id
        @param request: user email id
        @return: password reset link with jwt token
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data.get('email'))
        except User.DoesNotExist:
            return Response({'response': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
        email_data = {
            'user': user,
            'site': get_current_site(request).domain,
            'token': JWTAuth.getToken(username=user.username, password=user.password)
        }
        Email.sendEmail(Email.configurePasswordRestEmail(email_data))
        return Response({'response': 'Password reset link is sent to your mail'}, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def get(self, request, token):
        """This API is used to validate the jwt token present in the password reset link
        @param token: jwt token
        """
        jwtTokenData = JWTAuth.verifyToken(token)
        if jwtTokenData:
            return Response({'response': token}, status=status.HTTP_200_OK)
        return Response({'response': 'Invalid link found'}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, token):
        """This API is used to reset the user password after validating jwt token and its payload
        @param token: jwt token
        """
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        jwtData = JWTAuth.verifyToken(token)
        if jwtData:
            username = jwtData.get('username')
            password = jwtData.get('password')
        else:
            return Response({'response': 'Invalid link found'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(username=username)
            if password == user.password:
                user.set_password(raw_password=serializer.data.get('new_password'))
                user.save()
                return Response({'response': 'Your Password is reset'}, status=status.HTTP_200_OK)
            return Response({'response': 'Password does not match'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return Response({'response': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)
