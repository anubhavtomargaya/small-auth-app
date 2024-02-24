from datetime import datetime 
from datetime import timedelta
from flask import current_app as app
import json
import os
from pathlib import Path,PurePath
import pickle
import re
# from app import app

from .models import Transactions, RawTransactions
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from bs4 import BeautifulSoup
import base64
from .models import db
from playhouse.shortcuts import model_to_dict, dict_to_model
import pandas as pd
import logging
logger = logging.getLogger(__name__)
# logger.setLevel(logging.info)


def return_hello_as_html_tag(tag):
    return f"<{tag}> Hello </{tag}"


class CustomException(Exception):
    def __init__(self,message) -> None:
        super().__init__(message)


class QueryGenerator:

    # class ByLabel:
    #         def __init__(self,label) -> None:
    #             self.label = label

                
    def __init__(self) -> None:
        self.curr_date_time =datetime.utcnow()
        self.start_time = None
        self.end_time = None
        self.qry = None

   
    
    def get_last_n_days_mails_by_label(self,days,label='hdfc'):
        if label=='hdfc':
            self.start_time= self.curr_date_time.replace(minute=0,microsecond=0,hour=0,second=0)  + timedelta(days=1)
            self.end_time = self.curr_date_time -timedelta(days=days)
            qry = f""" 
            label:hdfc  after:{self.end_time.strftime('%Y-%m-%d')} before:{self.start_time.strftime('%Y-%m-%d')} 
            """
        
            self.qry=qry
            return qry

    def get_mails_by_date_range(self,start_date,end_date,label='hdfc'):
        if label=='hdfc':
            qry = f""" 
            label:hdfc  after:{start_date} before:{end_date} 
            """
            self.qry=qry
            return qry

#Connector object that manages token & builds service
class GmailConnector:
    def __init__(self) -> None:
        self.tokenFilePath = None
        self.creds = None
        self.credentials_file = None
        self.scopes = None
        self.service = None

    

    def buildService(self,token_file,credentials_file,SCOPES):  
        if os.path.exists(token_file):
            # Read the token from the file and store it in the variable self.self.creds
            with open(token_file, 'rb') as token:
                self.creds = pickle.load(token)
    
        # If credentials are not available or are invalid, ask the user to log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)
                print(self.creds)
    
            # Save the access token in token.pickle file for the next run
            with open(token_file, 'wb') as token:
                pickle.dump(self.creds, token)

        service = build('gmail', 'v1', credentials=self.creds)
        app.logger.info(f'service built...')
     
        return service

##Not being used
class RawThreads:
    def __init__(self) -> None:
        self.qry = None
        self.thread_ids:list = []
        self.size = None
        self.raw_messages = []
        self.msgs_size = None

    def get_thread_ids_from_qry(self,qry,service):
        result = pd.DataFrame(service.users().threads().list(userId='me',q= qry, maxResults=400).execute().get('threads', []))
        # print(f'result thread ids: {result["id"]}')
        # print('size',self.size)
        # self.thread_ids = list(result['id'])
        # self.size = len(self.thread_ids)
        # print('size',self.size)
        return result

    def get_messages_data_from_threads(self,service):
        for id in self.thread_ids:
            thread =  service.users().threads().get(userId='me', id=id).execute()
            messages_list = thread['messages']
            for msg in messages_list:
                self.raw_messages.append(msg) 
        self.msgs_size = len(self.raw_messages)
        return self.raw_messages




def queryForDateRange(start_date,end_date):
    qg = QueryGenerator()
    query= qg.get_mails_by_date_range(start_date,end_date,'hdfc')
    # print(query)
    app.logger.info('query generated: %s',query)
    return query

def saveEmailJSON(list_of_dict,stage,dt_range=None):
    

    try: 
        base_path = PurePath(__file__).parent
        output_folder = 'temp'

        if dt_range:
            date_part_in_filename = f'{dt_range[0]}_{dt_range[1]}'
        else:
            date_part_in_filename = datetime.now().strftime('%Y-%m-%d')
        if isinstance(list_of_dict,list) and stage!=3:
            app.logger.info('list  rcsv')

            count_of_items = len(list_of_dict)
            if stage==0:
                filename= f'emails_raw_{date_part_in_filename}_{count_of_items}_.json'
            elif stage==1:
                filename= f'emails_extracted_{date_part_in_filename}_{count_of_items}_.json'
            elif stage==2:
                filename= f'emails_txnInfo_{date_part_in_filename}_{count_of_items}_.json'
            else:
                pass
            app.logger.info('filename  %s',filename)
            filepath = Path(base_path,output_folder,filename)
            with open(filepath,'w' ) as f:
                json.dump(list_of_dict,f)
            return filename
            
        else: #stage ==3
            try:
                # app.debugger.logger.info('dataframe rcsv')
                count_of_items = list_of_dict.shape[0]
                # min_dt,max_dt= list_of_dict['date'].min(),list_of_dict['date'].max()
                filename= f'emails_finaltxn_{date_part_in_filename}_{count_of_items}_.csv'
                app.logger.info('filename  %s',filename)
                filepath = Path(base_path,output_folder,filename)
                app.logger.info('filepath  %s',filepath)
                list_of_dict.to_csv(filepath,index=False)
                return filename
            except:
                return False
            
    except Exception as e:
        return e
        

def get_messages_data_from_threads(service,ids):
    """
    service: gmail service built using token
    ids: list of thread Ids to process
    Appends all messages extracted from Threads into a list as RAW messages
    """

    messages_output=[]
    app.logger.info('thread IDs to process: %s',len(ids))
    if isinstance(ids,list):
        try:
            for id in ids:
                thread =  service.users().threads().get(userId='me', id=id).execute()
                messages_list = thread['messages']
                for msg in messages_list:
                    messages_output.append(msg) 
            app.logger.info('thread IDs yield %s messages',len(messages_output))
            return messages_output
        except Exception as e:
            app.logger.exception('unable to get messages for given thread id(s)')
            return e
    else:
        app.logger.exception('List of Ids expected')
        raise TypeError('List of Ids expected')
# #legacy
# def extractHTMLMimeType(payload,stage):
    
#     try:
#         countOfParts=len(payload['parts'])
#         msgSize =payload['body']['size']#do sth with msgsize Phase2
#     except Exception as e:
#         countOfParts=0
#         logger.exception('key error prolly')

#     if stage==1:

#         message_row = {"msgId":msg['id'],
#                         "threadId":msg['threadId'],
#                         "snippet":msg['snippet'],
#                         "mimeType":payload['mimeType'],
#                         "countOfParts":countOfParts,
#                         "msgSize":payload['body']['size'],
#                         "msgEpochTime":msg['internalDate'],
#                         "msgEncodedData":data,}

#         return message_row

#     elif stage==2:
#         message_row = {"msgId":msg['id'],
#                         "threadId":msg['threadId'],
#                         "snippet":msg['snippet'],
#                         # "mimeType":payload['mimeType'],
#                         # "countOfParts":countOfParts,
#                         # "msgSize":payload['body']['size'],
#                         "msgEpochTime":msg['internalDate'],
#                         "msgEncodedData":data,}

#         return message_row
    
#     elif stage==3:
#         message_row = {"msgId":msg['id'],
#                         "threadId":msg['threadId'],
#                         "msgEpochTime":msg['internalDate'],
#                         "msgEncodedData":data,}

#         return message_row

# def payloadDataMapper(data):
#     try:
#         message_row = {"msgId":msg['id'],
#                 "threadId":msg['threadId'],
#                 "snippet":msg['snippet'],
#                 # "mimeType":payload['mimeType'],
#                 # "countOfParts":countOfParts,
#                 # "msgSize":payload['body']['size'],
#                 "msgEpochTime":msg['internalDate'],
#                 "msgEncodedData":data,}

#         return message_row
#     except Exception as e:
#         app.logger.info("PayloadEMapperError")
#         pass

def extractCodedContentFromRawMessages(raw_messages_list:list):
    """Works like mapper for RAW MESSAGES
    Args:
        raw_messages_list (list): RAW returned by gmail service
    """
    
    app.logger.info('Input messages to process: %s',len(raw_messages_list))
    return_list = []
    for msg in raw_messages_list:
        app.logger.info('processing message: %s',msg['id'])
        try: #map and save
            payload = msg['payload']

            row = RawTransactions()
            row.msgId=msg['id']
            row.threadId=msg['threadId']
            row.snippet=msg['snippet']
            row.msgEpochTime=msg['internalDate']
            row.msghistoryId=msg['historyId']
   
            if payload['mimeType'] =='text/html':
                app.logger.info('mimeType found text/html')
                row.msgEncodedData = payload['body']['data']
                # row = payloadDataMapper(payldata)
                # messages_extracted_from_threads =extractHTMLMimeType(msg)
                # row.save()
                return_list.append(model_to_dict(row))
            else:
                app.logger.info('mimeType found as other, looping again')
                parts = payload['parts']
                for payld in parts:
                    if payld['mimeType'] =='text/html':
                        app.logger.info('mimeType found as text/html')
                        row.msgEncodedData = payld['body']['data']
                        # row.save()
                        # messages_extracted_from_threads =extractHTMLMimeType(data)
                        return_list.append(model_to_dict(row))
                    else:
                        app.logger.exception('No mime Type matched')   
        except Exception as e:
            app.logger.exception('MappingError: for the message id %s',msg['id'])
            return e
        
    app.logger.info('messages extracted %s \n messages given: %s',len(return_list),len(raw_messages_list))
    return return_list

def getContentsFromBody(ebd):
        amount_debtied = re.search(r'Rs.\d*', ebd)
        to_vpa = re.search(r'VPA.+?on', ebd)
        # date = re.search(r'\d{2}-\d{2}-\d{2}', ebd)
        # date = re.search(r'(\d{2}-\d{2}-\d{2}).*?\.', ebd)
        date = re.search(r'(\d{2}-\d{2}-\d{2}.*?)(?=\.)', ebd)

        
        if date:
            date = date.group(1)
        else: 
            date = None
        
        if to_vpa:
            to_vpa = to_vpa.group().strip('VPA  on')
        else: 
            to_vpa = None
        if amount_debtied:
            amount_debtied = amount_debtied.group().strip('Rs.')
        else: 
            amount_debtied = None
        
        return date,to_vpa,amount_debtied

def getEmailBody(coded_body):
    data = coded_body.replace("-","+").replace("_","/")
    decoded_data = base64.b64decode(data)
    soup = BeautifulSoup(decoded_data , "html.parser")
    # app.logger.info(soup)
    email_body = soup.find_all('td',{"class": "td"})[0].text
    if len(email_body) <20: #was taking an empty td as 0th element of list
        email_body = soup.find_all('td',{"class": "td"})[1].text
   
    return email_body
    # date,to_vpa,amount_debtied = getContentsFromBody(email_body)
    # return date,to_vpa,amount_debtied


def extractBodyFromEncodedData(coded_relevant_json):
    if not isinstance(coded_relevant_json,list):
        x=[]
        x.append(coded_relevant_json)
        coded_relevant_json=x
    else:
        pass
   
    try:
        app.logger.info('type of input %s',type(coded_relevant_json))
        count = len(coded_relevant_json)
        app.logger.info('size of input messages %s',count)
        decoded_extracted_info = []
        failed_first_box = []
        # coded_relevant_json=list(coded_relevant_json)
        for message in coded_relevant_json:
            # logger.info('message %s',message)
            try:

                data = message['msgEncodedData']
                # app.logger.info('processing json ')
                # date,to_vpa,amount_debtied = getEmailBody(data)
                email_body = getEmailBody(data)
                date,to_vpa,amount_debtied = getContentsFromBody(email_body)

                message['date']= date
                message['to_vpa']= to_vpa
                message['amount_debited']= amount_debtied
                del message['msgEncodedData']
                # if amount_debtied ==None or date==None or to_vpa==None:
                #     pass
                # else:
                decoded_extracted_info.append(message)
            except Exception as e:
                app.logger.exception('error extracting message id %s,',e)
                return ("ExtractionError:",e)

        app.logger.info('size of output messages %s',len(decoded_extracted_info))

        return decoded_extracted_info
            
    except Exception as e:
        # decoded_extracted_info
        logger.exception('error in extracting transaction info')
        return e

def buildGmailService():
    c=GmailConnector()
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    token_file = 'token.pickle' #accept at runtime
    credentials_file = 'creds.json' #load from config
    sr= c.buildService(token_file,credentials_file,SCOPES) #
    return sr #service

##WORKFLOW
def getMatchedThreadIdsForQuery(service,query):

    threads = service.users().threads().list(userId='me',q= query, maxResults=400).execute().get('threads', [])
    ids = [x['id'] for x in threads]
    app.logger.info('%s ids to be processed',len(ids))
    app.logger.info('ids: \n %s ',ids)
    return ids

def getDateRange(st_date,end_date):
    st =datetime.strftime( datetime.strptime(st_date,'%Y-%m-%d'),'%Y-%m-%d')
    et =datetime.strftime( datetime.strptime(end_date,'%Y-%m-%d'),'%Y-%m-%d')
    return st,et

##Instance #1 when request is for last day data only
# query = generateQueryForLastDay()


# st_dt,end_dt = getDateRange('2023-01-01','2023-03-31')
# dt_rng = (st_dt,end_dt)
# customQuery = queryForDateRange(st_dt,end_dt)


##Instance #2 when a bigger dump is required
# customQuery = queryForDateRange('2023-01-01','2023-03-31')
# WORKFLOW #2
def getQueryForDateRange(st,end):
    qg = QueryGenerator()
    query= qg.get_mails_by_date_range(st,end)
    logger.info('query generated.')
    return query
from .time_utils import get_timerange
def get_query_for_email(email='alerts@hdfcbank.net',):
        
        before,after = get_timerange()
        x = f"from:{email} after:{after} before:{before}"
        print(x,"qrt")
        return x

    

##WORKFLOW #1
def getQueryForLastDay():
    qg = QueryGenerator()
    query= qg.get_last_n_days_mails_by_label(days=1)
    logger.info('query generated.')
    print(query,"query")
    return query



def fetchRawMessagesForQuery(query):
    try:

        srvc = buildGmailService() #token
        app.logger.info('service built')
    except Exception as e:
        app.logger.exception('service not built')
        return e
    # app.logger.info('service %s  %s ',type(srvc),srvc)
    try:
        ids = getMatchedThreadIdsForQuery(srvc,query)
        app.logger.info('ids to process: %s ',ids)
        #independent of query after this point-
        messages = get_messages_data_from_threads(srvc,ids)
        app.logger.info('processed all messages: %s \n type : %s',len(messages),type(messages))
        ###DUMP TO S3
        return messages

    except Exception as e:
        return e



def processRawMessagesWithStages(raw_messages,stage):
    """_summary_

    Args:
        raw_messages (list): list of messages returned by fetchRawMessages
        stage (int): stage could be 0: raw messages as received 1: coded extracted from json >2: decoded format

    Returns:
        _type_: _description_
    """
    
    valid_stages = [0,1,2,3]
    if stage==0:
        logger.info('RAW stage requested..returning same as response')
        return raw_messages
    elif 0<stage<=3:
        try:
            app.logger.info('%s stage requested. Processing...',stage)
            coded_content_json = extractCodedContentFromRawMessages(raw_messages,stage)

            coded_content_json = model_to_dict(coded_content_json)
            app.logger.info('coded body extracted')
            if stage==1:
                return coded_content_json
            else:

                app.logger.info('decoding the coded body & extracting Transaction info')
                decoded_transaction_info = extractBodyFromEncodedData(coded_content_json) #big processing unit, split into chunks or make smaller
                app.logger.info('coded body extracted')
                if stage>=2:
                    return decoded_transaction_info

               
        except Exception as e:
            return "ExtractionError: "


    else:
        return ("InvalidArgument: stage:",stage,"valid_stages",valid_stages)


def cleanTransactionMessages(processed_messags):
    df = pd.DataFrame(processed_messags)
    # print(df.head())
    # print(meta)
    df.dropna(subset=['msgId','amount_debited'],inplace=True)
    df['amount_debited']= pd.to_numeric(df['amount_debited'], errors='coerce')
    # df['date'] =pd.to_datetime(df['date'],format='%d-%m-%Y')
    df['date'] = df['date'].apply(lambda x : datetime.strptime(x,'%d-%m-%y'))
    df = df.convert_dtypes(infer_objects=True)
    # print(df.dtypes)
    meta = {"rows":df.shape[0],
            "sum":sum(df['amount_debited'].to_list())}
    # print(df.columns)
    # print(meta)
    data = df.to_dict(orient='records')
    return data
# sr = buildGmailService()
# print(dt_rng)

# ids = getMatchedThreadIdsForQuery(sr,customQuery)

# #independent of query after this point-
# messages = get_messages_data_from_threads(sr,ids)

# print(saveEmailJSON(messages,stage=0,dt_range=dt_rng))
# print(messages) ##safa raw messages json extracted, independent of gmail service/user access after this point

def getCheckpointRawMessages(json_path):
    with open(json_path,'r') as f:
        raw_json = json.load(f)
    return raw_json

# messages = getCheckpointRawMessages('src/temp/emails_raw_2022-07-01_2022-09-30_325_.json')

# coded = processRawMessagesWithStages(messages,2)
# print(coded)
        
# coded_content_json = extractCodedContentFromRawMessages(messages)   
# print(saveEmailJSON(relevant_json,stage=1,dt_range=dt_rng))
# # print('relevant_json',relevant_json)
# print(saveEmailJSON(txn_info,stage=2,dt_range=dt_rng))
# txn_info=extractBodyFromEncodedData(coded_content_json)
# # print(txn_info)
# df =pd.DataFrame(txn_info)
# # df = df.sort_values(by=['msgEpochTime'],ascending=False)
# # print(df['date'].min(),
# # df['date'].max())
# print(df['msgEpochTime'].min(),
# df['msgEpochTime'].max())
# print(saveEmailJSON(df,3,dt_rng))
# # def saveOutputTxnDf(df):

# # df.to_csv('customQueryoutput.csv',index=False)
# # df.to_csv('output.csv',index=False)
# print(df)

def commitToDb(data):


    try:
        clean_messages = cleanTransactionMessages(processed_messags=data)
        app.logger.info("Messages Cleaned")
    except Exception as e:
        return ("CleaningError: %s ",e)

    if clean_messages:
        with db.atomic():
            res = Transactions.insert_many(data).execute()

        print(type(res))
        return res
    else:
        return "CommitError: Messages not clean"


##WORKFLOW #3
# def commitToDb(data):

#     rng = data['range']
#     response_checkpoint_level=data['stage']
#     st,et=rng[0],rng[1]
#     try:
#         rangeQuery = getQueryForDateRange(st,et)

#         app.logger.info('query: %s',rangeQuery)

#         messages = fetchRawMessagesForQuery(rangeQuery)  #token will go here

#     except Exception as e:
#         logger.exception('WorkflowError: %s',e)
#         return e

#     if response_checkpoint_level==0:
#         return messages
#     else:
#         pass  #to next try/catch
    
#     try:
#         app.logger.info('processing response for the stage %s',response_checkpoint_level)
#         processed_messages = processRawMessagesWithStages(messages,stage=response_checkpoint_level)  #give the stage argument to process up to the level
#         # return processed_messages

#     except Exception as e:
#         return ("ProcessingError: %s",e)

#     try:
#         clean_messages = cleanTransactionMessages(processed_messags=processed_messages)

#     except Exception as e:
#         return ("CleaningError: %s ",e)

#     if clean_messages:
#         with db.atomic():
#             res = Transactions.insert_many(data).execute()

#         print(type(res))
#         return 

