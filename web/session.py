#
# per-app session management
#

import flask


def session_get(app, key):
    return flask.session.get(app+'-'+key)


def session_set(app, key, value):
    flask.session.permanent = True # Safari seems to need this
    flask.session[app+'-'+key] = value


def session_pop(app, key):
    app_key = app+'-'+key
    if app_key in flask.session:
        flask.session.pop(app_key)
    

def session_pop_list(app, key_list):
    for k in key_list:
        app_key = app+'-'+k      
        if app_key in flask.session:
            flask.session.pop(app_key)


def remove_session_credentials(app):
    session_pop_list(app,
        ['auth_token', 'auth_token_secret', 'auth_redirect',
         'access_token', 'access_token_secret'])
    
