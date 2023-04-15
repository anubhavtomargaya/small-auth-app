from datetime import datetime 
from datetime import timedelta
import json
import os
from pathlib import Path,PurePath
import pickle
import re
from app import app
from models import Transactions
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import base64
# from playhouse.shortcuts import model_to_dict, dict_to_model
import pandas as pd
import logging
logger = logging.getLogger(__name__)
# logger.setLevel(logging.info)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
token_file = 'token.pickle' 
credentials_file = 'creds.json'
flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
return_token = flow.run_local_server(port=0)