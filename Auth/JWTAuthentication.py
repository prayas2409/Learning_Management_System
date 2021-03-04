import jwt
from decouple import config
from datetime import datetime, timedelta


class JWTAuth:
    """ This is used for getting token and verify token"""
    @staticmethod
    def getToken(username, password, secretKey=config('APP_SECRET_KEY')):
        """
        This function is used for getting user token
        :param username: user's username
        :param password: user password
        :param secretKey: App secrete key
        :return: return token
        """
        pay_load = {
            'username': username,
            'password': password,
            'exp': datetime.utcnow() + timedelta(days=2)
        }
        jwtToken = jwt.encode(pay_load, key=secretKey)
        return jwtToken

    @staticmethod
    def verifyToken(jwtToken, secretKey=config('APP_SECRET_KEY')):
        """
        This function is used for verify user token for authorization
        :param jwtToken: Token
        :param secretKey: App secrete key
        :return: verify token
        """
        try:
            verificationStatus = jwt.decode(jwtToken, key=secretKey, algorithms='HS256')
            return verificationStatus
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
