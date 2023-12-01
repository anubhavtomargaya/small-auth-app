from flask import current_app
import google.oauth2.credentials
from ..constants import CLIENT_ID,CLIENT_SECRET,ACCESS_TOKEN_URI
from .session_manager import is_logged_in,get_auth_token

## modify this to take auth tokens as input
def build_credentials():
    if not is_logged_in():
        current_app.logger.warning('user to be logged in')
        raise Exception('User must be logged in')

    oauth2_tokens = get_auth_token()
    if not oauth2_tokens:
        raise Exception("Cant get auth tokens") 
    
    return google.oauth2.credentials.Credentials(
                oauth2_tokens['access_token'],
                refresh_token=oauth2_tokens['refresh_token'],
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri=ACCESS_TOKEN_URI)