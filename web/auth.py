from functools import wraps
from session import session_get
from birdy.twitter import TwitterAuthError
from flask import url_for


def twitter_auth_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except TwitterAuthError:
            return url_for('auth_check')
    return wrapper


def get_twitter_credentials(app):
    access_token = session_get(app, 'access_token')
    access_token_secret = session_get(app, 'access_token_secret')
    if not (access_token and access_token_secret):     
        raise TwitterAuthError('User is not authorized')
    return {
        'access_token': access_token, 
        'access_token_secret': access_token_secret
    }


