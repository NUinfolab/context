"""
Flask session utilities
"""
import flask


def session_get(key):
    return flask.session.get(key)


def session_set(key, value):
    flask.session.permanent = True # Safari seems to need this
    flask.session[key] = value


def session_pop(key):
    if key in flask.session:
        flask.session.pop(key)
    

def session_pop_list(key_list):
    for k in key_list:  
        if k in flask.session:
            flask.session.pop(k)


def remove_session_credentials():
    session_pop_list(['auth_token', 'auth_token_secret', 
        'auth_redirect', 'access_token', 'access_token_secret'])
    
