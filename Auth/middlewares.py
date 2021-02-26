from .JWTAuthentication import JWTAuth
from rest_framework import status
from django.http import JsonResponse
from django.urls import reverse
from .models import User
import sys
sys.path.append('..')
from LMS.cache import Cache

class TokenAuthentication(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        token = request.headers.get('Authorization')
        if token :
            jwtData = JWTAuth.verifyToken(token)
            cache = Cache.getCacheInstance()
            cache_token = None
            try:
                cache_token = cache.hget(jwtData.get('username'), 'auth')
            except Exception:
                pass
            if cache_token:
                cache_token = cache_token.decode('utf-8')
            if jwtData and cache_token == token:
                user = User.objects.get(username=jwtData.get('username'))
                request.META['user'] = user
                return self.get_response(request, *args, **kwargs)
        return JsonResponse({'response': 'You have to login to access this resource',
                             'path': f"{reverse('login')}?next={request.path}"}, status=status.HTTP_401_UNAUTHORIZED)


class CantAccessAfterLogin(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, token=None):
        token = request.headers.get('Authorization')
        jwtData = JWTAuth.verifyToken(token)
        cache = Cache.getCacheInstance()
        cache_token = None
        try:
            cache_token = cache.hget(jwtData.get('username'), 'auth')
        except Exception:
            pass

        if cache_token:
            cache_token = cache_token.decode('utf-8')    
        if jwtData and cache_token == token:
            return JsonResponse({'response': 'You need to logout to access this this resource'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return self.get_response(request, token)