import jwt
import logging
import datetime
import string
from random import choices

from passlib.hash import pbkdf2_sha256
from functools import wraps
from flask import abort, request
from utils.web_key import PRIVATE_WEB_KEY
from utils.web_key_pub import PUBLIC_WEB_KEY

TEN_YEARS = 60 * 60 * 24 * 7 * 52 * 10
ONE_YEARS = (60 * 60 * 24 * 7 * 52)
ONE_HOUR = 60 * 60
HALF_A_DAY = 60 * 60 * 12

TOKEN_ALGO = 'RS512'


def extract_payload(token):
    try:
        payload = jwt.decode(token, PUBLIC_WEB_KEY, algorithm=TOKEN_ALGO)
        return payload
    except jwt.ExpiredSignatureError as e:
        logging.error(str(e) + " ExpiredSignatureError")
        raise
    except jwt.InvalidTokenError as e:
        logging.error(str(e) + " InvalidTokenError")
        raise
    except Exception as e:
        logging.error(str(e) + " Error")
        raise
    return False


"""
    Flask decorator for your sensitive API endpoint.
"""


def authentication_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(403, 'User not logged or no token received')
        token = request.headers['Authorization']
        token = token.split('Bearer ')
        if len(token) > 1:
            token = token[1]
        else:
            abort(403, 'Empty token')
        try:
            payload = extract_payload(token)
        except Exception:
            abort(403, 'User not logged or session expired')
        else:
            return f(user=payload, *args, **kwargs)
    return decorated_function


def is_admin(paylaod):
    return paylaod.get('is_admin', False)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            abort(403, 'User not logged or no token received')
        token = request.headers['Authorization']
        token = token.split('Bearer ')
        if len(token) > 1:
            token = token[1]
        else:
            abort(403, 'Empty token')
        try:
            payload = extract_payload(token)
        except Exception:
            abort(403, 'User not logged or session expired')
        else:
            if payload['is_admin'] is True:
                return f(user=payload, *args, **kwargs)
            else:
                abort(403, 'User is not an admin')
    return decorated_function


"""
    Generate a JWT token for the CLIENT SIDE. User can READ but nor modify the token
"""


def generate_user_token(username, is_admin=False):
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(seconds=HALF_A_DAY)

    payload = {
        # Reserved claims
        'iat': now,
        'nbf': now,
        'exp': now + delta, # expiration de la session client coté client ou serveur ?
        'iss': 'ARBA',
        # 'aud': audience
    }
    payload['username'] = username
    payload['is_admin'] = is_admin
    payload['userid'] = ''.join(choices(string.ascii_letters + string.digits, k=20))

    return jwt.encode(payload, PRIVATE_WEB_KEY, algorithm=TOKEN_ALGO).decode('utf-8')


"""
    Utilities function for psw/token generation. fuck yeah love cosmic algo
"""


def hash_password(password):
    return pbkdf2_sha256.encrypt(password, rounds=1000000, salt_size=16)


def verify_password(xhash, password):
    return pbkdf2_sha256.verify(password, xhash)
