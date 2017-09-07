import jwt
import datetime
import json

from passlib.hash import pbkdf2_sha256
from functools import wraps
from flask import abort, request
from calendar import timegm
from utils.web_key import PRIVATE_WEB_KEY
from utils.web_key_pub import PUBLIC_WEB_KEY

TEN_YEARS = 60 * 60 * 24 * 7 * 52 * 10
ONE_YEARS = 60 * 60 * 24 * 7 * 52
ONE_HOUR = 60 * 60

TOKEN_ALGO = 'RS512'
PUBLIC_MASTER_KEY = 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCjhgga9+VB9o+cQdvu7ZBzkGmySN6+uwFMLb84Q6eBU0lIRLPlPYJ7iMAeOWheLyA3CnjsVZdgt0NLEb+NmSkOUisyhur8AFjwx5LNQreZX4maMBHLQUJy7+4fFSokHc9U/ue8nmw2XmJ+Xh0BsoyEkJs+VpDt21lazIazgBTcdN0/zrYrcXNKUQQAz3cB9+Nc7JuL3+X3+Liknp1+T1Cr0NuMXbwV88O20db4b6ulwZ/IYNu1R2ldPGRvDfcyDaq4A52n5znWHCoaSUoPUAfi8KSnTf/wt+Lur29W5yq6TU7bWBcdd3X2h7vAGRnfDEgVULIAnYoI3wc7FetTyH7v'


def extract_payload(token):
    try:
        payload = jwt.decode(token, PUBLIC_MASTER_KEY, algorithm=TOKEN_ALGO)
        return payload
    except jwt.ExpiredSignatureError, e:
        print(str(e)+" ExpiredSignatureError")
        raise
    except jwt.InvalidTokenError, e:
        print(str(e)+" InvalidTokenError")
        raise
    except Exception, e:
        print(str(e)+" Error")
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
            jwt.decode(token, PUBLIC_WEB_KEY, algorithm=TOKEN_ALGO)
        except Exception, e:
            abort(403, 'User not logged or session expired')
        else:
            return f(*args, **kwargs)
    return decorated_function

"""
    Generate a JWT token for the CLIENT SIDE. User can READ but nor modify the token
"""
def generate_user_token(username):
    now = datetime.datetime.utcnow()
    delta = datetime.timedelta(seconds=ONE_HOUR)

    payload = {
        # Reserved claims
        'iat': now,
        'nbf': now,
        'exp': now + delta,
        'iss': 'ARBA',
        #'aud': audience
    }
    payload['username'] = username

    return jwt.encode(payload, PRIVATE_WEB_KEY, algorithm=TOKEN_ALGO)

"""
    Utilities function for psw/token generation. fuck yeah love cosmic algo
"""
def hash_password(password):
    return pbkdf2_sha256.encrypt(password, rounds=1000000, salt_size=16)

def verify_password(xhash, password):
    return pbkdf2_sha256.verify(password, xhash)
