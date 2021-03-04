from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from .serializer import *
from .permissions import isAdmin
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate
from .JWTAuthentication import JWTAuth
from django.utils.decorators import method_decorator
from .middlewares import TokenAuthentication, CantAccessAfterLogin
from django.contrib.auth.hashers import check_password
from .models import User, TokenBlackList, Roles
from django.db import IntegrityError
from .tasks import send_registration_mail, send_password_reset_mail
import sys

sys.path.append('..')
from LMS.loggerConfig import log
from Management.utils import GeneratePassword
from LMS.cache import Cache
import datetime
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from LMS.mailConfirmation import Email


class AddRoleAPIView(GenericAPIView):
    """ This API is used for adding role """
    serializer_class = RoleSerializer
    queryset = Roles.objects.all()

    def get(self, request):
        """
        This function is used for fetching all the roles
        :return: roles
        """
        try:
            roles = Roles.objects.all()
            serializer = self.serializer_class(roles, many=True)
            log.info("Roles are retrieved")
            return Response({'response': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            log.error(e)
            return Response({'response': 'Something went wrong'})

    def post(self, request):
        """This API is used to add role by the admin
        @param request: role_name,
        @return: save role in the database
        """
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            try:
                serializer.save()
            except IntegrityError as e:
                log.error(e)
                return Response({'response': f"{serializer.data.get('role')} role is already present"},
                                status=status.HTTP_400_BAD_REQUEST)
            log.info('Role is added')
            return Response({'response': f"{serializer.data.get('role')} role is added"},
                            status=status.HTTP_201_CREATED)
        except Exception as e:
            log.error(e)
            return Response({'response': 'Something went wrong'})


@method_decorator(TokenAuthentication, name='dispatch')
class UserRegistrationView(GenericAPIView):
    """ This API is used to Register the User """
    serializer_class = UserSerializer
    permission_classes = (isAdmin,)

    def post(self, request):
        """This API is used to Add user like Mentor,Engineer or another Admin to the system by an Admin
         and informs the user about their account creation via email
         :request params : user related data like username, name, email etc
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get('username')
        first_name = serializer.data.get('first_name')
        last_name = serializer.data.get('last_name')
        email = serializer.data.get('email')
        mobile = serializer.data.get('mobile')
        roles = serializer.data.get('role')
        role = Roles.objects.get(id=roles)
        password = GeneratePassword.generate_password(self)
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                        email=email, mobile=mobile, role=role, password=password)

        data = {
            'name': user.get_full_name(),
            'username': user.username,
            'password': password,
            'email': user.email,
            'site': get_current_site(request).domain,
        }
        send_registration_mail.delay(data)
        log.info(f"Registration is done and mail is sent to {request.data['email']}")
        return Response(
            {'response': f"A new {role.role} is registered successfully"},
            status=status.HTTP_201_CREATED)


@method_decorator(CantAccessAfterLogin, name='dispatch')
class UserLoginView(GenericAPIView):
    """ This API is used to logged in the user"""
    serializer_class = UserLoginSerializer

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
        if user:
            role = user.role
            user.last_login = str(datetime.datetime.now())
            user.save()
            log.info('successful login')
            response = Response(
                {'response': f'You are logged in successfully', 'username': username, 'role': role.role},
                status=status.HTTP_200_OK)
            jwt_token = JWTAuth.getToken(username=username, password=password)
            response['Authorization'] = jwt_token
            # token is storing in redis cache
            cache = Cache.getCacheInstance()
            cache.hmset(username, {'auth': jwt_token})
            cache.expire(username, time=datetime.timedelta(days=2))
            return response
        log.info('bad credential found')
        return Response({'response': 'Bad credential found'}, status=status.HTTP_401_UNAUTHORIZED)


@method_decorator(TokenAuthentication, name='dispatch')
class UserLogoutView(GenericAPIView):
    """ This Logout API used to logged out the user """
    serializer_class = UserLoginSerializer

    def get(self, request):
        """This API is used to log user out and to clear the user session
        """
        cache = Cache.getCacheInstance()
        user = request.META.get('user')
        if user:
            cache.delete(user.username)  # deleting redis cache
        log.info('logout successful')
        return Response({'response': 'You are logged out'}, status=status.HTTP_200_OK)


@method_decorator(TokenAuthentication, name='dispatch')
class ChangeUserPasswordView(GenericAPIView):
    """ This API is used to change the user password """
    serializer_class = ChangeUserPasswordSerializer

    def put(self, request):
        """This API is used to change user password
        @request_params = old password, new password and confirm password
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
    """ This API is used to send reset password link when user forgot password """
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
        except User.DoesNotExist as e:
            log.error(e)
            return Response({'response': 'Email not found'}, status=status.HTTP_404_NOT_FOUND)
        email_data = {
            'name': user.get_full_name(),
            'email': user.email,
            'site': get_current_site(request).domain,
            'token': JWTAuth.getToken(username=user.username, password=user.password)
        }
        send_password_reset_mail.delay(email_data)
        log.info('reset password link is sent to mail')
        print(email_data['token'])
        return Response({'response': 'Password reset link is sent to your mail'}, status=status.HTTP_200_OK)


@method_decorator(CantAccessAfterLogin, name='dispatch')
class ResetPasswordView(GenericAPIView):
    """ This API used to reset the password"""
    serializer_class = ResetPasswordSerializer

    def put(self, request):
        """This API is used to reset the user password after validating jwt token and its payload
        @param token: jwt token
        """
        token = request.GET.get('token')
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
        except User.DoesNotExist as e:
            log.error(e)
            return Response({'response': 'User not found!'}, status=status.HTTP_404_NOT_FOUND)
