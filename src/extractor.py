

# from flask import Request, current_app
from datetime import datetime ,timedelta
# from workflow import GmailConnector
from gmail_fetcher import RawMessage,GmailConnector,GmailFetcher
import logging  
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
import re
import base64
from bs4 import BeautifulSoup
from abc import ABC

from playhouse.shortcuts import model_to_dict, dict_to_model


class CodedMsg(object):
    """stage 1 data seperated from payload object
    """
    def __init__(self,rm:RawMessage) -> None:
        self.id=rm.id
        self.data = None
        self.threadId = rm.threadId
        self.snippet = rm.snippet
        self.internalDate = rm.internalDate
        self.payload = rm.payload
        self.historyId = rm.historyId

    def extractData(self):
        if self.payload['mimeType'] =='text/html':
            logger.info('mimeType found text/html')
            self.data = self.payload['body']['data']
            return True
        else:
            logger.info('mimeType found as other, looping again')
            parts = self.payload['parts']
            for payld in parts:
                if payld['mimeType'] =='text/html':
                    logger.info('mimeType found as text/html')
                    self.data = payld['body']['data']
                    return True
                else:
                    logger.exception('No mime Type matched')   
                    return False
        
    def getEmailBody(self):
        data = self.data.replace("-","+").replace("_","/")
        decoded_data = base64.b64decode(data)
        soup = BeautifulSoup(decoded_data , "html.parser")
        # current_app.logger.info(soup)
        email_body = soup.find_all('td',{"class": "td"})[0].text
        if len(email_body) <20: #was taking an empty td as 0th element of list
            email_body = soup.find_all('td',{"class": "td"})[1].text
    
        return email_body



    def getContentsFromBody(self,ebd):
        try:
            amount_debtied = re.search(r'Rs.\d*', ebd)
            to_vpa = re.search(r'VPA.+?on', ebd)
            date = re.search(r'\d{2}-\d{2}-\d{2}', ebd)
            credit = re.search(r'Credit Card', ebd)
          
            if date:
                date = date.group()
            else: 
                date = None
            
            if to_vpa:
                mode = 'UPI'
                to_vpa = to_vpa.group().strip('VPA  on')
            else: 
                to_vpa = None
                if credit:
                    mode = 'CC'
                
            if amount_debtied:
                amount_debtied = amount_debtied.group().strip('Rs.')
            else: 
                amount_debtied = None
            
            return date,to_vpa,amount_debtied,mode
        
        except Exception as e:
            return "RegexError:",e

class DecodedTransaction():
    def __init__(self,cm:CodedMsg,d,v,a,m) -> None:
        self.date= d
        self.vpa = v 
        self.amt = a
        self.mode = m
        self.msgId = cm.id
        self.msgEpochTime = cm.internalDate
        self.snippet = cm.snippet
        self.threadId = cm.threadId
        self.historyId = cm.historyId
    




class Extractor(object):
    def __init__(self) -> None:
        self.raw_message = None
        self.coded_msg = None
        self.decoded_msg = None
  
    def extract(self,rm):
        self.raw_message=rm
        logger.info('processing message: %s',self.raw_message.id)
        cm = CodedMsg(rm=self.raw_message)
        cm.extractData()
        ebd =cm.getEmailBody()
        d,v,a,m = cm.getContentsFromBody(ebd)
        dc = DecodedTransaction(cm,d,v,a,m)
        # self.decoded_msg=dc
            
        # logger.info('messages extracted %s \n messages given: %s',len( self.coded_msg_list ),len(self.raw_messages_list))
        return dc

# e = GmailFetcher()
# e.main('2023-07-15','2023-07-21') #fetch raw messages [RawMessage]
# ls = e.messages_output
# ex  = Extractor(ls[0])
# cms = ex.extract()
# print(cms,cms.__dict__)
# print(e.messages_output[0].__dict__)

