# """
# module to signin using google
# https://www.mattbutton.com/2019/01/05/google-authentication-with-python-and-flask/
# """


# import functools
# import json
# import os
# import flask 
# from flask import current_app, url_for
# import logging
# # logger= logging.getLogger(__name__)
# # logger.setLevel(logging.INFO)
# from authlib.client import OAuth2Session
# import google.oauth2.credentials
# import googleapiclient.discovery
# from gmail_fetcher import GmailQuery

# ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
# # "https://oauth2.googleapis.com/token"
# AUTHORIZATION_URL ='https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
# # "https://accounts.google.com/o/oauth2/auth"
# AUTHORIZATION_SCOPE =["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
# # 'openid email profile'
# # ['https://www.googleapis.com/auth/gmail.readonly','openid','email']

# AUTH_REDIRECT_URI ="http://localhost:5000/google/auth"
# #  os.environ.get("FN_AUTH_REDIRECT_URI", default=False)
# BASE_URI =   "http://localhost:5000/"
# BASE_REDIRECT_URI =   "http://localhost:5000/fetch"
# # os.environ.get("FN_BASE_URI", default=False)
# CLIENT_ID = "483124533702-0mgvs24ebsuj9f9gaetbv8vgv7mrn333.apps.googleusercontent.com"
# # os.environ.get("FN_CLIENT_ID", default=False)
# CLIENT_SECRET = "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"
# # os.environ.get("FN_CLIENT_SECRET", default=False)

# AUTH_TOKEN_KEY = 'auth_token'
# AUTH_STATE_KEY = 'oauth_state'

# app = flask.Blueprint('google_auth', __name__)

# def is_logged_in():
#     return True if AUTH_TOKEN_KEY in flask.session else False

# def build_credentials():
#     if not is_logged_in():
#         current_app.logger.warning('user to be logged in')
#         raise Exception('User must be logged in')

#     oauth2_tokens = flask.session[AUTH_TOKEN_KEY]
    
#     return google.oauth2.credentials.Credentials(
#                 oauth2_tokens['access_token'],
#                 # refresh_token=oauth2_tokens['refresh_token'],
#                 client_id=CLIENT_ID,
#                 client_secret=CLIENT_SECRET,
#                 token_uri=ACCESS_TOKEN_URI)

# def get_matched_emails(query:GmailQuery):
#     try:
#         current_app.logger.info('building gmail client')
#         credentials = build_credentials()

#         gmail_client = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
       
#         threads = gmail_client.users().threads().list(userId='me',q= query, maxResults=400).execute()
       
#         return threads
#     except Exception as e:
#         current_app.logger.exception('running gmail query failed')
#         return flask.jsonify(e)
    
# def get_thread_by_id(id):
#     try:
#         current_app.logger.info('getting thread by id %s:',id)
#         credentials = build_credentials()

#         gmail_client = googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)
       
#         thread =  gmail_client.users().threads().get(userId='me', id=id).execute()

       
#         return thread
#     except Exception as e:
#         current_app.logger.exception('getting thread failed')
#         return flask.jsonify(e)
    

# def get_user_info():
    
#     try:
#         current_app.logger.info('building credentials')
#         credentials = build_credentials()

#         oauth2_client = googleapiclient.discovery.build(
#                             'oauth2', 'v2',
#                             credentials=credentials)
#         return oauth2_client.userinfo().get().execute()
#     except Exception as e:
#         current_app.logger.exception('building credentials failed')
#         return flask.jsonify(e)

# def get_user_threads(query):
    
#     try:
#         app.logger.info('building credentials')
#         credentials = build_credentials()

#         oauth2_client = googleapiclient.discovery.build(
#                             'gmail', 'v1',
#                             credentials=credentials)
#         return  oauth2_client.users().threads().list(userId='me',q= query, maxResults=400).execute().get('threads', [])
#     except Exception as e:
#         app.logger.exception('building credentials failed')
#         return flask.jsonify(e)


# def no_cache(view):
#     @functools.wraps(view)
#     def no_cache_impl(*args, **kwargs):
#         response = flask.make_response(view(*args, **kwargs))
#         response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
#         response.headers['Pragma'] = 'no-cache'
#         response.headers['Expires'] = '-1'
#         return response

#     return functools.update_wrapper(no_cache_impl, view)

# @app.route('/google/login')
# @no_cache
# def login():
#     current_app.logger.error("RUNNING LOGIN")
#     current_app.logger.info('building session')
#     session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
#                             scope=AUTHORIZATION_SCOPE,
#                             redirect_uri=AUTH_REDIRECT_URI)
  
#     uri, state = session.authorization_url(AUTHORIZATION_URL)
#     current_app.logger.error("state %s",state )
#     current_app.logger.error("uri %s",uri)
#     flask.session[AUTH_STATE_KEY] = state
#     flask.session.permanent = True
#     a =flask.session[AUTH_STATE_KEY] 
#     current_app.logger.info("keys!! %s",flask.session.keys())
#     current_app.logger.info("state key!! %s",flask.session[AUTH_STATE_KEY])
#     # current_app.logger.info("flask session:",  a)
    

#     return flask.redirect(uri, code=302)

# @app.route('/google/auth')
# @no_cache
# def google_auth_redirect():
#     current_app.logger.info("keys!! %s",flask.session.keys())
#     req_state = flask.request.args.get('state', default=None, type=None)
#     current_app.logger.info('state!!: %s',req_state)
#     # if req_state != flask.session[AUTH_STATE_KEY]:
#     #     response = flask.make_response('Invalid state parameter', 401)
#     #     return response
#     try:
#         current_app.logger.info('creating session')
#         session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
#                                 scope=AUTHORIZATION_SCOPE,
#                                 state=req_state,
#                                 redirect_uri=AUTH_REDIRECT_URI)
#     except Exception as e:
#         return flask.jsonify(e)
#     current_app.logger.info('session')
        
#     oauth2_tokens = session.fetch_access_token(
#                         ACCESS_TOKEN_URI,            
#                         authorization_response=flask.request.url)

#     flask.session[AUTH_TOKEN_KEY] = oauth2_tokens
#     current_app.logger.info('oath tokens!! : %s',type(oauth2_tokens))

#     return flask.redirect(url_for('google_auth.etc',data=oauth2_tokens), code=307)

# @app.route('/google/logout')
# @no_cache
# def logout():
#     flask.session.pop(AUTH_TOKEN_KEY, None)
#     flask.session.pop(AUTH_STATE_KEY, None)

#     return flask.redirect(BASE_URI, code=302)

# import ast
# import pathlib
# @app.route('/google/etc')
# def etc():
    
#     d=flask.request.args['data']
   
#     d = ast.literal_eval(d)
#     current_app.logger.info('body: %s',d)
#     current_app.logger.info('type: %s',type(d))
#     if is_logged_in():
#         user_info = get_user_info()
#         current_app.logger.info(user_info)
#         name=user_info['given_name']
#         expiresat=d['expires_at']
#         val=d['access_token'][0:6]
#         # curr_pth = pathlib.Path(__file__).resolve().parent
#         # tkdir = pathlib.Path('temp','etc')
#         # filename=f'token_{name}_{val}_{expiresat}_.json'
      
#         # filepath = pathlib.Path(curr_pth,tkdir,filename)
#         # with open(filepath,'w') as f:
#             # print(json.dump(dew,f))
        
#         ###check if not able to save file in ec2

#         return flask.redirect(BASE_URI, code=302)
#     # '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
#     else:
#         # return render_template("index.html")

#         return flask.jsonify("ERORROR )")

