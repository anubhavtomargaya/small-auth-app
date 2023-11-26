


from flask import Request, current_app
# from datetime import datetime ,timedelta
# from workflow import GmailConnector
# from gconn import GmailConnector
import logging  
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logger = current_app.logger
from abc import ABC

class RawMessage(object):
    def __init__(self,m) -> None:
        self.id=m['id']
        self.labelIds = m['labelIds']
        self.threadId = m['threadId']
        self.snippet = m['snippet']
        self.payload = m['payload']
        self.sizeEstimate = m['sizeEstimate']
        self.historyId = m['historyId']
        self.internalDate = m['internalDate']
    


from googleapiclient.discovery import build

class GmailQuery(object):
    """give start and end time in date format '%Y-%m-%d'
    by default __str__ returns a label query with the date range
    """
      
    def __init__(self,start_,end_,from_=None,label_='hdfc') -> None:
        # self.curr_date_time =datetime.utcnow()
        self.start_time = start_
        self.end_time = end_
        self.label=label_
        self.from_email = from_
        self.qry_tmp =  """ 
            {}:{}  after:{} before:{} 
            """
    def get_label_query(self):
        if self.label:
            return self.qry_tmp.format('label',self.label,self.start_time,self.end_time)
        else:
            return False
            
    def get_from_query(self):
        if self.from_email:
            return self.qry_tmp.format('from',self.from_email,self.start_time,self.end_time)
        else:
            return False
        
    def __str__(self) -> str:
        return self.get_label_query()



class GmailFetcher:
    def __init__(self,token=None) -> None:
        self.token = token
        self.gmail_service  = None
        self.ids =[]
        self.messages_output=[]
        self.qry = None


    def getMatchedThreadIdsForQuery(self,query:GmailQuery):

        try:
            threads = self.gmail_service.users().threads().list(userId='me',q= query, maxResults=400).execute().get('threads', [])
       
        except Exception as e:
            raise e
        if isinstance(threads,list):
            ids = [x['id'] for x in threads]
            matched_threads = len(ids)
            logger.info('%s ids to be processed',matched_threads)
            logger.info('ids: \n %s ',ids)
            self.ids=ids
            return True
        else:
            raise 
    
    def get_messages_data_from_threads(self):
        """
        service: gmail service built using token
        ids: list of thread Ids to process
        Appends all messages extracted from Threads into a list as RAW messages
        """

        
        logger.info('thread IDs to process: %s',len(self.ids))
        if isinstance(self.ids,list):
            try:
                for id in self.ids:
                    thread =  self.gmail_service.users().threads().get(userId='me', id=id).execute()
                    messages_list = thread['messages']
                    for msg in messages_list:
                        rm = RawMessage(msg)
                        self.messages_output.append(rm) 
                logger.info('thread IDs yield %s messages',len(self.messages_output))
                return self.messages_output
            except Exception as e:
                logger.exception('unable to get messages for given thread id(s)')
                return e
        else:
            logger.exception('List of Ids expected')
            raise TypeError('List of Ids expected')
    
    def fetch(self,st,et,creds=None):
        """generates the query using st,et; builds gmail service using stored token and credentials. 
        fetches the matched ids from gmail. fetches raw message for all the messages contained in threads.


        Args:
            st (str): %Y-%m-%d
            et (str):  %Y-%m-%d

        Returns:
            list: list of RawMessage object 
        """
        q = GmailQuery(st,et,from_='alerts@hdfcbank.net')
        print(q.__str__())
        logger.info('query generated: %s',q.__str__())
        self.qry = q.__str__()
        if creds:
            logger.info('building gmail client')
            logger.info('building gmail client')
            self.service = build('gmail', 'v1', credentials=creds)
        
            
        else:pass
    
            # try:
            #     if self.token:
            #         cn = GmailConnector() #token
            #         self.gmail_service = cn.buildClientFromToken(self.token)
            #         logger.info('service built')
            #     else:
            #         c=GmailConnector()
            #         token_file = 'token.pickle' 
            #         self.gmail_service= c.buildService(token_file) #

            # except Exception as e:
            #     logger.exception('gmail client not built')
            #     return e
        # app.logger.info('service %s  %s ',type(srvc),srvc)
        try:
            if not self.gmail_service:
                raise ValueError("Cant find service!!")
            
            ids = self.getMatchedThreadIdsForQuery(q)
            logger.info('ids to process: %s ',ids)
            #independent of query after this point-
            self.get_messages_data_from_threads()
            logger.info('processed all messages: %s \n type : %s',len(self.messages_output),type(self.messages_output))
            ###DUMP TO S3
            return self.messages_output 

        except Exception as e:
            return e

    



# q = GmailQuery('2023-07-15','2023-07-21',from_='alerts@hdfcbank.net')
# print(q.__str__())

# # print(e.buildGmailService())
# # print(e.getMatchedThreadIdsForQuery(q.__str__()))
# # print(e.ids)


# e = GmailFetcher()
# e.fetch('2023-07-15','2023-07-21')
# print(e.messages_output[0].__dict__)
# print(e.ids)
# print(RawMessage(e.messages_output[0]))