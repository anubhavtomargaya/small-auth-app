

from flask import current_app as app
from src.blueprints.gmail.workflow import getContentsFromBody, getEmailBody
import logging
logger = logging.getLogger(__name__)

def extractBodyFromEncodedData(coded_relevant_json):
    """ not giving a shit about the previous function or the global stage param, just
        needs the key msgEncodedData to be there fks off to do the job 
    """
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