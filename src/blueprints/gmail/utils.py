from flask import current_app as app, jsonify
from ...common.utils import build_credentials
from googleapiclient.discovery import build

def get_matched_threads(query,
                     maxResults:int=400):   
    try:
        app.logger.info('building credentials')

        oauth2_client = build(
                            'gmail', 'v1',
                            credentials=build_credentials())
        if not oauth2_client :
            raise Exception("Unable to build oauth client for gmail")
        
        return  oauth2_client.users().threads().list(userId='me',q= query, maxResults=maxResults).execute().get('threads', [])
    except Exception as e:
        app.logger.exception('building credentials failed')
        return jsonify(e)
