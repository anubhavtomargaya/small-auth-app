from flask import current_app as app, jsonify
from ...common.google_utils import build_credentials
from googleapiclient.discovery import build

def get_matched_threads(query,
                     maxResults:int=400):   
    try:
        app.logger.info('building credentials')

        oauth2_client = build(
                            'gmail','v1',
                            credentials=build_credentials())
        if not oauth2_client :
            raise Exception("Unable to build oauth client for gmail")
        
        threads = oauth2_client.users().threads().list(userId='me',q= query, maxResults=maxResults)
        thread_list = threads.execute().get('threads',[])
        # print(threads)
        # print(thread_list)
        # print("threads  ")
        return  [x['id'] for x in thread_list]
    except Exception as e:
        app.logger.exception('building credentials failed')
        return jsonify(e)
    
def get_messages_data_from_threads(ids):
    """
    service: gmail service built using token
    ids: list of thread Ids to process
    Appends all messages extracted from Threads into a list as RAW messages
    """

    messages_output=[]
    app.logger.info('thread IDs to process: %s',len(ids))
    if isinstance(ids,list):
        try:
            oauth2_client = build(
                            'gmail','v1',
                            credentials=build_credentials())
            if not oauth2_client :
                raise Exception("Unable to build oauth client for gmail")
        
            for id in ids:
                thread =  oauth2_client.users().threads().get(userId='me', id=id).execute()
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
    
