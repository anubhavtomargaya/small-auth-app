from flask import  current_app, jsonify
from ...constants import *
from .utils import build_credentials
import googleapiclient.discovery


def get_user_info():
    try:
        current_app.logger.info('Building credentials')
        credentials = build_credentials()
        oauth2_client = googleapiclient.discovery.build('oauth2', 'v2', credentials=credentials)
        return oauth2_client.userinfo().get().execute()
    except Exception as e:
        current_app.logger.exception('Building credentials failed')
        return jsonify(e)