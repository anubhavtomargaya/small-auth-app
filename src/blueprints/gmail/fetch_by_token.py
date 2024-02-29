

import datetime
import json
from flask import jsonify
from src.common.common_utils import get_now_time_string, get_random_execution_id
from src.common.db_handler import insert_execution_metadata,insert_raw_transactions

from src.common.db_init import PipelineExecutionMeta
from .query import get_query_for_email
from .utils import get_matched_threads, get_messages_data_from_threads
# from process_encoded import extractBodyFromEncodedData
from .process_raw import extractCodedContentFromRawMessages


class TokenFetchRequest:
    def __init__(self,
                 token,
                 start,
                 end,
                 email='alerts@hdfcbank.net') -> None:
        
        self.token = token
        self.start = start
        self.end = end
        self.email = email
        
# def start_pipeline(gmail_query:str='test', 
#                    user_id='me'):
    
#     """Starts a new pipeline, creates a corresponding entry in PipelineExecutionMeta,
#       and returns the execution ID."""
#     # Start time (replace with actual logic for getting current time)
#     start_time = datetime.datetime.now()

#     # Create a new execution metadata entry
#     execution_meta = PipelineExecutionMeta.create(
#         gmail_query=gmail_query,
#         start_time=start_time,
#         user_id=user_id,
#     )

#     return execution_meta.execution_id
from src.common.models import MetaEntry


def fetch_for_token(request:TokenFetchRequest):
    """ insert into database the raw transaction encoded msg format
    also update the """
    if not isinstance(request,TokenFetchRequest):
        raise TypeError("Invalid input")
    #validate token
    meta_entry = MetaEntry(execution_id=get_random_execution_id(),
                           start_time=get_now_time_string(),
                           )
    mailbox_query = get_query_for_email(start=request.start,end=request.end)
    meta_entry.query=mailbox_query
    thread_ids =  get_matched_threads(mailbox_query,token=request.token) #log output 
    meta_entry.thread_count = len(thread_ids)

    email_msgs_list = get_messages_data_from_threads(thread_ids,token=request.token)
    meta_entry.email_message_count = len(email_msgs_list)
    raw_coded_msgs = extractCodedContentFromRawMessages(email_msgs_list)
    print(raw_coded_msgs[0],"raw msgs")
    print(raw_coded_msgs[0].keys(),"raw msgs")
    db_response = insert_raw_transactions(raw_coded_msgs)
    print("db res",db_response)
    #insert these into db as RawTransactions

    meta_entry.raw_message_count =  len(raw_coded_msgs)
    meta_entry.end_time = get_now_time_string()
    meta_entry.status = "SUCCESS"

    insert_execution_metadata(meta_entry)
    return  jsonify(json.dumps(raw_coded_msgs) )


if __name__ == '__main__':
    

    """ expected token format in TokenFetchRequest:"""
    sample_token = {'access_token': 'ya29.a0AfB_byCyywmiQtN4ufGZVC--XINWOaG8RHorBSR-ZWWRfLWKFD6fWzNAbdEPj2fW7mV_WCxNrADH1gdHIIAZqEdjeN8eS6XtCngcosMgXpc7_SIjydFkKCAPbqvMpiA7ZcccA6oNMT__zIL7pVsALt57bBxOGZqRP8W9aCgYKATkSARISFQHGX2MiX5ss9_IOR_shtGMB5mqB0A0171', 'expires_at': 1708978287, 'expires_in': 3599, 'id_token': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjU1YzE4OGE4MzU0NmZjMTg4ZTUxNTc2YmE3MjgzNmUwNjAwZThiNzMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0ODMxMjQ1MzM3MDItMG1ndnMyNGVic3VqOWY5Z2FldGJ2OHZndjdtcm4zMzMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0ODMxMjQ1MzM3MDItMG1ndnMyNGVic3VqOWY5Z2FldGJ2OHZndjdtcm4zMzMuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDM2NjYyMDAxNTQxMTY3NzQ5MzUiLCJlbWFpbCI6ImltYW51YmhhdjE4QGdtYWlsLmNvbSIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJhdF9oYXNoIjoiVnFJS3k1QTltc3RBYThILUF0TzltUSIsIm5hbWUiOiJBbnViaGF2IFRvbWFyIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0pXNEhCcGw1dFFBRDFTcWo5Mm1NZUNnRF9POGVBX2c1RFNKUjg5Zmp1MFZIND1zOTYtYyIsImdpdmVuX25hbWUiOiJBbnViaGF2IiwiZmFtaWx5X25hbWUiOiJUb21hciIsImxvY2FsZSI6ImVuLUdCIiwiaWF0IjoxNzA4OTc0Njg4LCJleHAiOjE3MDg5NzgyODh9.k0p4lNyPT_vI2gLlFVP7evVr9Z8PJg3o7rKUnvbwXzGfkMhJjiiaH7sSr8NpAlwqFWDuO4ZrKetzC7s9QugAmcBy1jjcxt2ZTg5Ouv9Us91GqNRIlbwCYr87OT2L9K56H6IT2z_jeGi-XpDFdq7aDSrM3ZDoulP_pSr10WO3DwuBNjepcmMiJexuspdCTPUCYodt8MuvwzWzyPUBzM565UH6jlf6CNfaVCKKQoC31URFatEqn_GDqWz0PbUPqjwQp6qfh1qUHCNoiVwD8avajIRAHWzVWId0O249KDP7JxhBw6uikx0KWinfpAHDvbLKnBO_zmw6GHRkt900viSGqw', 'refresh_token': '1//0g2fx5fS0ZZNNCgYIARAAGBASNwF-L9Iri8d0aIats_a-9kniIHIufltNXj67WlJ-HDuZTqFWchdDIYLPIvAXYf6WFLOB6OEbEVk', 'scope': 'openid https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/gmail.readonly', 'token_type': 'Bearer'}
    sample_request = TokenFetchRequest(token=sample_token,
                                    start='2024-02-23',
                                    end='2024-02-27',
                                    email=None)
    data = fetch_for_token(sample_request)
    print(data)