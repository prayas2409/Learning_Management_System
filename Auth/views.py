from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import GenericAPIView
from .serializers import UserSerializer, UserLoginSerializer
from .permissions import isAdmin
import sys
sys.path.append('..')
from LMS.mailConfirmation import Email
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login, logout
from .JWTAuthentication import JWTAuth

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
            request.session['username'] = JWTAuth.getToken(username=username, password=password)
            return Response({'response': 'You are logged in'}, status=status.HTTP_200_OK)
        return Response({'response': 'Bad credential found'}, status=status.HTTP_401_UNAUTHORIZED)

