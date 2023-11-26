from flask import  current_app
from ...constants import *
import googleapiclient.discovery

from ...common.utils import build_credentials

def get_user_info():
    try:
        current_app.logger.info('Building credentials')
        credentials = build_credentials()
        oauth2_client = googleapiclient.discovery.build('oauth2',
                                                        'v2',
                                                        credentials=credentials)
        return oauth2_client.userinfo().get().execute()
    except Exception as e:
        current_app.logger.exception('Building credentials failed')
        return e