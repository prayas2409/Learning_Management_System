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
from .middlewares import TokenAuthentication, TokenAuthenticationOnFirstAccess, CantAccessAfterLogin
from django.contrib.auth.hashers import check_password
from .models import User, TokenBlackList
import random
from django.urls import reverse
from .tasks import send_registration_mail, send_password_reset_mail
import sys
sys.path.append('..')
from LMS.mailConfirmation import Email
from LMS.loggerConfig import log
from Management.utils import GeneratePassword
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@method_decorator(TokenAuthentication, name='dispatch')
class UserRegistrationView(GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (isAdmin,)

    def get(self, request):
        """This API is used to inform the client that the request is genuine and the client can serve the registration page
        @return: return genuine Admin request
        """
        log.info('Admin Request for Add user API')
        return Response({'response': 'Admin request'}, status=status.HTTP_202_ACCEPTED)

    def post(self, request):
        """This API is used to Add user like Mentor,Engineer or another Admin to the system by an Admin
         and informs the user about their account creation via email
         request parms : user related data like username, name, email etc
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        first_name = serializer.data.get('first_name')
        last_name = serializer.data.get('last_name')
        email = serializer.data.get('email')
        mobile = serializer.data.get('mobile')
        role = serializer.data.get('role')
        password = GeneratePassword.generate_password(self)
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                        email=email, mobile=mobile, role=role, password=password)
        data = {
            'name': user.get_full_name(),
            'username': user.username,
            'password': password,
            'role': user.role,
            'email': user.email,
            'site': get_current_site(request).domain,
            'token': JWTAuth.getToken(username=user.username, password=user.password)
        }
        send_registration_mail.delay(data)
        log.info(f"Registration is done and mail is sent to {request.data['email']}")
        return Response({'response': f"A new {request.data['role']} is added", 'username': username, 'password': password,
                         'token': data['token']}, status=status.HTTP_201_CREATED)


@method_decorator(CantAccessAfterLogin, name='dispatch')
class UserLoginView(GenericAPIView):
    serializer_class = UserLoginSerializer
    token_param_config = openapi.Parameter('token',in_=openapi.IN_QUERY,description='Description',type=openapi.TYPE_STRING)

    def get(self, request, token=None):
        """This API is used to inform the client that its a genuine login request and it can serve the login interface
        @param request: login request
        @return: informs client about genuine request
        """
        if not request.META.get('user'):
            token = request.GET.get('token')
            try:
                blacklist_token = TokenBlackList.objects.get(token=token)
            except TokenBlackList.DoesNotExist:
                blacklist_token = None
            if blacklist_token:
                log.info('This login link is already used')
                return Response({'response': 'This link is already used'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            log.info('Valid login page request')
            return Response({'response ': ' User can login'}, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def post(self, request, token=None):
        """This API is used to log user in
        @param request: basic credential
        @return: logs user in
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        password = serializer.data.get('password')
        user = authenticate(request, username=username, password=password)
        role = user.role
        if user:
            if user.last_login == None and user.is_superuser == False:
                token = request.GET.get('token')
                if JWTAuth.verifyToken(token):  
                    log.info('login successful but need to change password')
                    response = Response({'response': 'You are logged in! Now you need to change password to access resources',
                                        'role': role,
                                    'link': reverse('change-password-on-first-access',
                                                                                args=[token])}, status=status.HTTP_200_OK)
                    response['Authorization'] = JWTAuth.getToken(username=username, password=password)
                    return response
                log.info('Need to use the link shared in mail')
                return Response({'response': 'You need to use the link shared in your mail for the first time'},
                                status=status.HTTP_401_UNAUTHORIZED)

            user.last_login = str(datetime.datetime.now())
            user.save()
            log.info('successful login')
            response = Response({'response': f'You are logged in as {role}'}, status=status.HTTP_200_OK)
            response['Authorization'] = JWTAuth.getToken(username=username, password=password)
            return response
        log.info('bad credential found')
        return Response({'response': 'Bad credential found'}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(TokenAuthentication, name='dispatch')
class UserLogoutView(GenericAPIView):
    def get(self, request):
        """This API is used to log user out and to clear the user session
        """
        # if request.session.get(request.META['user'].username):
        #     request.session.pop(request.META['user'].username)
        # logout(request)
        log.info('logout successful')
        return Response({'response': 'You are logged out'}, status=status.HTTP_204_NO_CONTENT)


@method_decorator(TokenAuthentication, name='dispatch')
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
        if check_password(old_password, request.META['user'].password):
            request.META['user'].set_password(raw_password=serializer.data.get('new_password'))
            request.META['user'].save()
            log.info('password changed successfully')
            return Response({'response': 'Your password is changed successfully!'}, status=status.HTTP_200_OK)
        log.info('Old password does not match')
        return Response({'response': 'Old password does not match!'}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(CantAccessAfterLogin, name='dispatch')
class ForgotPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, token=None):
        """This API is used to send reset password link to user email id
        @param request: user email id
        @return: password reset link with jwt token
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(email=serializer.data.get('email'))
        except User.DoesNotExist:
            log.info("email id not found")
            return Response({'response': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
        email_data = {
            'name': user.get_full_name(),
            'email': user.email,
            'site': get_current_site(request).domain,
            'token': JWTAuth.getToken(username=user.username, password=user.password)
        }
        send_password_reset_mail.delay(email_data)
        log.info('reset password link is sent to mail')
        return Response({'response': 'Password reset link is sent to your mail'}, status=status.HTTP_200_OK)


@method_decorator(CantAccessAfterLogin, name='dispatch')
class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def get(self, request, token):
        """This API is used to validate the jwt token present in the password reset link
        @param token: jwt token
        """
        try:
            blacklist_token = TokenBlackList.objects.get(token=token)
        except TokenBlackList.DoesNotExist:
            blacklist_token = None
        if blacklist_token:
            log.info('This link is already used')
            return Response({'response': 'This link is already used'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        jwtTokenData = JWTAuth.verifyToken(token)
        if jwtTokenData:
            return Response({'response': token}, status=status.HTTP_200_OK)
        log.info('invalid link request')
        return Response({'response': 'Invalid link found'}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, token):
        """This API is used to reset the user password after validating jwt token and its payload
        @param token: jwt token
        """
        try:
            blacklist_token = TokenBlackList.objects.get(token=token)
        except TokenBlackList.DoesNotExist:
            blacklist_token = None
        if blacklist_token:
            log.info('This link is already used')
            return Response({'response': 'This link is already used'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.serializer_class(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        jwtData = JWTAuth.verifyToken(token)
        if jwtData:
            username = jwtData.get('username')
            password = jwtData.get('password')
        else:
            log.info('Invalid link request')
            return Response({'response': 'Invalid link found'}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(username=username)
            if password == user.password:
                user.set_password(raw_password=serializer.data.get('new_password'))
                user.save()
                TokenBlackList.objects.create(token=token)
                log.info('Password is reset')
                return Response({'response': 'Your Password is reset'}, status=status.HTTP_200_OK)
            log.info('password does not match')
            return Response({'response': 'Password does not match'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            log.info('User not found')
            return Response({'response': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)


@method_decorator(TokenAuthenticationOnFirstAccess, name='dispatch')
class ChangePasswordOnFirstAccess(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def get(self, request, token):
        """This API is used to validate the chnage_password_on_first_login link and to inform client whether the
        client should serve the page or not
        @param token: jwt token
        @return: validates the link
        """
        try:
            blacklist_token = TokenBlackList.objects.get(token=token)
        except TokenBlackList.DoesNotExist:
            blacklist_token = None
        if blacklist_token:
            log.info('This link is already used')
            return Response({'response': 'This link is already used'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if JWTAuth.verifyToken(token):
            log.info('valid link')
            return Response({'response': 'link is Valid'}, status=status.HTTP_202_ACCEPTED)
        log.info('invalid link')
        return Response({'response': 'link is invalid'}, status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, token):
        """This API is used to change user password on first access
        @request_parms : new password and confirm password
        @rtype: saves new password in database and allows to access other resources
        """
        try:
            blacklist_token = TokenBlackList.objects.get(token=token)
        except TokenBlackList.DoesNotExist:
            blacklist_token = None
        if blacklist_token:
            log.info('This link is already used')
            return Response({'response': 'This link is already used'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        if JWTAuth.verifyToken(token):
            request.META['user'].set_password(raw_password=serializer.data.get('new_password'))
            request.META['user'].last_login = str(datetime.datetime.now())
            request.META['user'].save()
            TokenBlackList.objects.create(token=token)
            log.info('password is changed successfully')
            return Response({'response': 'Your password is changed successfully! Now You can access resources'},
                                status=status.HTTP_200_OK)
        log.info('This link is expired')
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
            log.info('This mail id is not registered')
            return Response({'response': 'This Mail id is not registered'}, status=status.HTTP_404_NOT_FOUND)
        if user and user.last_login != None:
            password = GeneratePassword.generate_password(self)
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
            log.info('new login link is shared on mail')
            return Response({'response': 'New login link is shared on your mail','token':data['token']}, status=status.HTTP_200_OK)
        log.info('not applicable for this user')
        return Response({'response': 'Not applicable for you!'}, status=status.HTTP_406_NOT_ACCEPTABLE)