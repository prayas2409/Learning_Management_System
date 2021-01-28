from django.shortcuts import redirect
from .JWTAuthentication import JWTAuth


class SessionAuthentication(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not JWTAuth.verifyToken(request.session.get(request.user.username)):
            return redirect('/user/login/')
        return self.get_response(request)
