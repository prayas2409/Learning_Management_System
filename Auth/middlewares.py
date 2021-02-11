from .JWTAuthentication import JWTAuth
from rest_framework import status
from django.http import JsonResponse
from django.urls import reverse
from .models import User


class TokenAuthentication(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        jwtData = JWTAuth.verifyToken(request.headers.get('Authorization'))
        if request.resolver_match.url_name == 'logout':
            return self.get_response(request, *args, **kwargs)
        if jwtData:
            user = User.objects.get(username=jwtData.get('username'))
            request.META['user'] = user
            if not user.last_login != None or user.is_superuser:
                return self.get_response(request, *args, **kwargs)
            return JsonResponse({'response': 'You need to change password to access this resource'},
                                status=status.HTTP_403_FORBIDDEN)
        return JsonResponse({'response': 'You have to login to access this resource',
                             'path': f"{reverse('login')}?next={request.path}"}, status=status.HTTP_401_UNAUTHORIZED)


class TokenAuthenticationOnFirstAccess(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, token):
        jwtData = JWTAuth.verifyToken(request.headers.get('Authorization'))
        if jwtData:
            user = User.objects.get(username=jwtData.get('username'))
            request.META['user'] = user
            return self.get_response(request, token)
        return JsonResponse({'response': 'You are not logged in!'}, status=status.HTTP_403_FORBIDDEN)


class CantAccessAfterLogin(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, token=None):
        if JWTAuth.verifyToken(request.headers.get('authorization')):
            return JsonResponse({'response': 'You need to logout to access this this resource'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        return self.get_response(request, token)