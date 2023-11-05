
from datetime import datetime 
from datetime import timedelta
from flask import current_app
import json
import os
from pathlib import Path,PurePath
import pickle
import re
from app import app
from models import Transactions, RawTransactions
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import base64
from models import db
from playhouse.shortcuts import model_to_dict, dict_to_model
import pandas as pd
import logging
logger = logging.getLogger(__name__)

# logger.setLevel(logging.info)
#Connector object that manages token & builds service
class GmailConnector:
    def __init__(self) -> None:
        self.tokenFilePath = None
        self.creds = None
        self.credentials_file = 'creds.json' #load from config
        self.scopes =['https://www.googleapis.com/auth/gmail.readonly']
        self.service = None

    def build_client_from_credential_obj(self,credentails):
        return build('gmail', 'v1', credentials=credentails)
    
    def buildClientFromToken(self,token):
        try:
            self.creds = token
            service = build('gmail', 'v1', credentials=self.creds)
            return service
        except Exception as e:
            logger.info('not get')
            return e

    

    
    def buildService(self,token_file):  
        if os.path.exists(token_file):
            # Read the token from the file and store it in the variable self.self.creds
            with open(token_file, 'rb') as token:
                self.creds = pickle.load(token)
    
        # If credentials are not available or are invalid, ask the user to log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scopes)
                self.creds = flow.run_local_server(port=0)
                print(self.creds)
    
            # Save the access token in token.pickle file for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(self.creds, token)

        service = build('gmail', 'v1', credentials=self.creds)
        app.logger.info(f'service built...')
     
        return service
