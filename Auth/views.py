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
from .middlewares import SessionAuthentication, SessionAuthenticationOnFirstAccess, CantAccessAfterLogin
from django.contrib.auth.hashers import check_password
from .models import User
import random
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
            'site': get_current_site(request).domain,
            'token': JWTAuth.getToken(username=request.data['username'], password=request.data['password'])
        }
        Email.sendEmail(Email.configureAddUserEmail(data))
        return Response({'response': f"A new {request.data['role']} is added"}, status=status.HTTP_201_CREATED)


class UserLoginView(GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        """This API is used to log user in
        @param request: basic credential
        @return: logs user in
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        password = serializer.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_first_time_login:
                token = request.GET.get('token')
                if JWTAuth.verifyToken(token):
                    login(request, user)
                    return Response({'response': 'You are logged in! Now you need to change password to access resources',
                                     'token': token}, status=status.HTTP_200_OK)
                return Response({'response': 'You need to use the link shared in your mail for the first time'},
                                status=status.HTTP_401_UNAUTHORIZED)
            login(request, user)
            request.session[username] = JWTAuth.getToken(username=username, password=password)
            return Response({'response': 'You are logged in'}, status=status.HTTP_200_OK)
        return Response({'response': 'Bad credential found'}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(SessionAuthentication, name='dispatch')
class UserLogoutView(GenericAPIView):
    def get(self, request):
        """This API is used to log user out and to clear the user session
        """
        if request.session.get(request.user.username):
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


@method_decorator(SessionAuthenticationOnFirstAccess, name='dispatch')
class ChangePasswordOnFirstAccess(GenericAPIView):
    serializer_class = ChangeUserPasswordSerializer

    def get(self, request, token):
        """This API is used to validate the chnage_password_on_first_login link and to inform client whether the
        client should serve the page or not
        @param token: jwt token
        @return: validates the link
        """
        if JWTAuth.verifyToken(token):
            return Response({'response': 'link is Valid'}, status=status.HTTP_202_ACCEPTED)
        return Response({'response': 'link is invalid'}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, token):
        """This API is used to change user password on first access
        @request_parms = old password, new password and confirm password
        @rtype: saves new password in database and allows to access other resources
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        old_password = serializer.data.get('old_password')
        if JWTAuth.verifyToken(token):
            if check_password(old_password, request.user.password):
                request.user.set_password(raw_password=serializer.data.get('new_password'))
                request.user.is_first_time_login = False
                request.user.save()
                return Response({'response': 'Your password is changed successfully! Now You can access resources'},
                                status=status.HTTP_200_OK)
            return Response({'response': 'Old password does not match!'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'response': 'This link is expired'}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(CantAccessAfterLogin, name='dispatch')
class RequestNewLoginLinkWithTokenView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        """This API is used to generate new login link with token if the first link sent by the admin gets expired
        @param request: user email
        @return: sends new link to user email
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'response': 'This Mail id is not registered'}, status=status.HTTP_404_NOT_FOUND)
        if user and user.is_first_time_login:
            password = str(random.randint(100000, 999999))
            user.set_password(raw_password=password)
            user.save()
            data = {
                'name': user.get_full_name(),
                'username': user.username,
                'password': password,
                'role': user.role,
                'email': user.email,
                'site': get_current_site(request).domain,
                'token': JWTAuth.getToken(username=user.username, password=user.password)
            }
            Email.sendEmail(Email.configureAddUserEmail(data))
            return Response({'response': 'New login link is shared on your mail'}, status=status.HTTP_200_OK)
        return Response({'response': 'Not applicable for you!'}, status=status.HTTP_406_NOT_ACCEPTABLE)