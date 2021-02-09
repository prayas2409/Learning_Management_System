from .JWTAuthentication import JWTAuth
from rest_framework import status
from django.http import JsonResponse
from django.urls import reverse


class SessionAuthentication(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        jtwData = JWTAuth.verifyToken(request.session.get(request.user.username))
        if request.user.is_authenticated:
            if request.resolver_match.url_name == 'logout':
                return self.get_response(request, *args, **kwargs)
            if jtwData:
                return self.get_response(request, *args, **kwargs)
            return JsonResponse({'response': 'You need to change password to access this resource'},
                                status=status.HTTP_403_FORBIDDEN)
        return JsonResponse({'response': 'You have to login to access this resource',
                             'path': f"{reverse('login')}?next={request.path}"}, status=status.HTTP_401_UNAUTHORIZED)


class SessionAuthenticationOnFirstAccess(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, token):
        jtwData = JWTAuth.verifyToken(token)
        if jtwData and request.user.is_authenticated:
            return self.get_response(request, token)
        return JsonResponse({'response': 'You are not logged in!'}, status=status.HTTP_403_FORBIDDEN)


class CantAccessAfterLogin(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, token=None):
        if request.user.is_authenticated:
            return JsonResponse({'response': 'You need to logout to access this this resource'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        return self.get_response(request, token)