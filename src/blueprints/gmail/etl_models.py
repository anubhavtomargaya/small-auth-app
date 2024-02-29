from typing import Optional

class User:
    def __init__(self,
                 uid,
                 logindttm,
                 token,
                 email,
                 latesthistoryid) -> None:
        self.uid = uid
        self.logindttm = logindttm
        self.token = token
        self.email = email
        self.latesthistoryid = latesthistoryid

class PipelineExecutionMeta:
    def __init__(self,
                 executionid,
                 gmailquery,
                 starttime,
                 endtime,
                 threadcount,
                 emailmessagecount,
                 rawmessagecount,
                 decodedmessagecount,
                 ) -> None:
        
        self.executionid =  executionid
        self.gmailquery = gmailquery
        self.starttime =  starttime
        self.endtime =  endtime
        self.threadcount =  threadcount
        self.emailmessagecount =  emailmessagecount
        self.rawmessagecount =  rawmessagecount
        self.decodedmessagecount =  decodedmessagecount

    

# Input Model (Simplified based on provided code and assumptions)
class EmailMessage:
    """ msgs recvd from thread """
    def __init__(self, 
                msg_id,
                thread_id,
                snippet,
                msg_epoch_time):
        
        self.msg_id = msg_id
        self.thread_id = thread_id
        self.snippet = snippet
        self.msg_epoch_time = msg_epoch_time

class RawMessage(EmailMessage):
    """ encoded data found after recursing through parts """
    def __init__(self,
                msg_id,
                thread_id,
                snippet,
                msg_epoch_time,
                msg_encoded_data):
        
        super().__init__(msg_id,
                         thread_id,snippet,
                         msg_epoch_time)
        
        self.msg_encoded_data = msg_encoded_data

# 
class Message(RawMessage):
    """ extracted data is the date,amt,vpa class extracted by regex """
    def __init__(self,
                msg_encoded_data: str):
        
        self.msg_encoded_data: str = msg_encoded_data
        self.extracted_data = None

# Output Model in txndata
class ExtractedData:
    def __init__(self,
                date: Optional[str],
                to_vpa: Optional[str],
                amount_debtied: Optional[str]):
        
        self.date: Optional[str] = date
        self.to_vpa: Optional[str] = to_vpa
        self.amount_debtied: Optional[str] = amount_debtied


            