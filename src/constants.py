ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
# "https://oauth2.googleapis.com/token"
AUTHORIZATION_URL ='https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'
# "https://accounts.google.com/o/oauth2/auth"
AUTHORIZATION_SCOPE =["https://www.googleapis.com/auth/gmail.readonly","https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"]
# 'openid email profile'
# ['https://www.googleapis.com/auth/gmail.readonly','openid','email']

AUTH_REDIRECT_URI ="http://localhost:5000/google/auth"
#  os.environ.get("FN_AUTH_REDIRECT_URI", default=False)
BASE_URI =   "http://localhost:5000/"
BASE_REDIRECT_URI =   "http://localhost:5000/fetch"
# os.environ.get("FN_BASE_URI", default=False)
CLIENT_ID = "483124533702-0mgvs24ebsuj9f9gaetbv8vgv7mrn333.apps.googleusercontent.com"
# os.environ.get("FN_CLIENT_ID", default=False)
CLIENT_SECRET = "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"
# os.environ.get("FN_CLIENT_SECRET", default=False)

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'oauth_state'