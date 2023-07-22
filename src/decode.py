

from flask import Request, current_app
from datetime import datetime ,timedelta

import logging  
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
import re
import base64
from bs4 import BeautifulSoup
from abc import ABC



from gmail_fetcher import GmailFetcher,RawMessage
from extractor import Extractor

def decode(rm_list):
    if isinstance(rm_list,list):
        ls = rm_list    
    elif isinstance(rm_list,RawMessage):
        ls = [rm_list]
        print('single')
    else:
        return False

    # logger.info("messages to process %s",isinstance(list))
    logs = []
    txns = []
    for rm_dict in ls:
        current_app.logger.info(RawMessage(rm_dict))
        rm = RawMessage(rm_dict)
        try:
            
            row = (rm.threadId,rm.id, rm.snippet)
            ex  = Extractor()
            txn = ex.extract(rm)
            row = row + ("S",)
            logs.append(row)
            # print(txn.__dict__)
            txns.append(txn)
            print(txn.msgId)

        except Exception as e:
            row = row + ("F",)
            logs.append(row)
            pass
       
    # print(len(logs),logs[0])
    # print(len(txns),txns[0].__dict__)
    return txns


def test_decode():

## fetch a range of emails
    fetcher = GmailFetcher()

    fetcher.fetch('2023-07-15','2023-07-21') #fetch raw messages [RawMessage]

    ls = fetcher.messages_output
    print(len(fetcher.ids))
    print(len(ls))
    print(decode(ls[0])[0].__dict__)
