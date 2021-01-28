import jwt
from decouple import config
from datetime import datetime, timedelta


class JWTAuth:
    @staticmethod
    def getToken(username, password, secretKey=config('APP_SECRET_KEY')):
        pay_load = {
            'username': username,
            'password': password,
            'exp': datetime.utcnow() + timedelta(days=2)
        }
        jwtToken = jwt.encode(pay_load, key=secretKey)
        return jwtToken

    @staticmethod
    def verifyToken(jwtToken, secretKey=config('APP_SECRET_KEY')):
        try:
            verificationStatus = jwt.decode(jwtToken, key=secretKey, algorithms='HS256')
            return verificationStatus
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
