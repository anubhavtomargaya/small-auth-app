from flask import session
FLAST_NEXT_URL_KEY = 'next_url' 
# session.permanent=True
AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'oauth_state'


def set_auth_token(token):
    session[AUTH_TOKEN_KEY] = token

def get_auth_token():
    return session.get(AUTH_TOKEN_KEY, None)

def set_auth_state(state):
    session['permanent'] = True
    session[AUTH_STATE_KEY] = state

def get_auth_state():
    return session.get(AUTH_STATE_KEY, None)

def clear_auth_session():
    session.pop(AUTH_TOKEN_KEY, None)
    session.pop(AUTH_STATE_KEY, None)

def is_logged_in():
    return AUTH_TOKEN_KEY in session

##next url for redirection

def set_next_url(url):
    session[FLAST_NEXT_URL_KEY] = url

def get_next_url(default_url=None):
        return session.get(FLAST_NEXT_URL_KEY, default_url)

def clear_next_url():
        session.pop(FLAST_NEXT_URL_KEY, None)

def get_session_keys():
    return list(session.keys())

def get_session_items():
    return list(session.items())