from src.blueprints.gmail.process_encoded import extractBodyFromEncodedData
from src.blueprints.gmail.process_raw import extractCodedContentFromRawMessages, parse_gmail_message
from . import gmail_app
import requests,json,datetime
from flask import current_app,jsonify,request, url_for, redirect,render_template
from ...common.session_manager import get_auth_token, is_logged_in,set_next_url
from ..google_auth.auth import get_user_info
from .query import get_query_for_email
from .utils import get_matched_threads, get_messages_by_thread_ids, get_messages_data_from_threads
from .gmail_fetcher import GmailFetcher
from src.blueprints.gmail.fetch_by_token import fetch_for_token,TokenFetchRequest
RAW_MESSAGE_COUNT= None
stats_dict = {
        "MAILBOX_THREAD_COUNT" :None,
        "MAILBOX_MESSAGE_COUNT" : None,
        "RAW_MESSAGE_COUNT":None,
        "TRANSACTION_MESSAGE_COUNT":None
        }

@gmail_app.route('/',methods=['GET','POST'])
def index():
    if not is_logged_in():
        set_next_url(url_for('gmail_app.index'))
        current_app.logger.debug("not logged int")
        return redirect(url_for('google_auth.login'))
    else:
        current_app.logger.debug("logged int")
        return render_template('home.html') ##gmail_app > index.html

## get gmail emails and put in cache / db 
## works in stages 
# 1. GmailMessages 2. BS64Content 3. Transaction 
# 4. txn_extra_dimensions
#defaults.py
FM_EMAIL = 'alerts@hdfcbank.net'
RANGE_STR = 'lastDay'

class FetchRequest:
    def __init__(self,
                 start_date:str,
                 end_date:str,
                 from_email:str=FM_EMAIL,
                 history_id:int=None,
                 session_token=None) -> None:
        
        self.st = start_date
        self.et = end_date
        self.from_email = from_email
        self.history_id=history_id
        self.session_token = session_token

@gmail_app.route('/stats/',methods=['GET']) 
def get_last_load_stats():
    return jsonify(stats_dict)

@gmail_app.route('/fetch/',methods=['GET','POST']) 
def fetchTransactionEmailsFromGmail():
    params = ['range_str','stage']
    start_time = datetime.datetime.utcnow()
    mthd = request.method 
    args = request.args

    current_app.logger.info('query: %s',mthd)
 
    if mthd == 'GET':
        current_app.logger.info('args: %s',args)
        ###read arguements
        if is_logged_in():
            if args.get('range_str'):
                query_range_str = args.get('range_str') #1
            else:
                    st='2024-02-21'
                    et='2024-02-28'
                    token = get_auth_token()
                    rq = TokenFetchRequest(token=token,
                                    start=st,
                                    end=et)
                    return fetch_for_token(rq) #tested using token as input instead of from session
                    rangeQuery = get_query_for_email(start=st,end=et)
                    threads = get_matched_threads(rangeQuery)
                    stats_dict['MAILBOX_THREAD_COUNT'] = len(threads)
                # current_app.logger.info(d)
                    print("returning")
                    msgs = get_messages_data_from_threads(threads)
                    stats_dict['MAILBOX_MESSAGE_COUNT'] = len(msgs)
                    print(threads)
                    # coded_msgs = [parse_gmail_message(msg) for msg in msgs]
                    coded_msgs = extractCodedContentFromRawMessages(msgs)
                    stats_dict['RAW_MESSAGE_COUNT'] = len(coded_msgs)
                    #put this into db, along w count
                    transactions_ = extractBodyFromEncodedData(coded_msgs)
                    stats_dict['TRANSACTION_MESSAGE_COUNT'] = len(transactions_)

                    return  jsonify(json.dumps(transactions_) )

            # return jsonify("MissingArgument: Arguements 'range' missing")

            print("res",response_checkpoint_level)
            if args.get('stage'):
                response_checkpoint_level = int(args.get('stage')) #2
                current_app.logger.info('setting response stage from stage argument as %s',response_checkpoint_level)
            else:
                response_checkpoint_level=0
                print("res",response_checkpoint_level)
                current_app.logger.info('setting response stage as 0, i.e: RAW')
            
            ###fetch messages for range param from gmail & return based on requested stage
            if query_range_str=='lastDay':
                try:
                    lastDayQuery = getQueryForLastDay()
                    current_app.logger.info('query: %s',lastDayQuery)
                    messages = fetchRawMessagesForQuery(lastDayQuery) 
                    current_app.logger.info('msgs: %s',type(messages))
                    if messages:
                        pass
                    else:
                        return jsonify("FetchingError ")

                except Exception as e:
                    logger.exception('WorkflowError: %s',e)
                    return jsonify("FetchingError %s",e)

                if response_checkpoint_level==0:
                    return jsonify(messages)
                else:
                    pass  #to next try/catch
                
                ##process messages received as RAW
                try:
                    current_app.logger.info('processing response for the stage %s',response_checkpoint_level)
                    processed_messages = processRawMessagesWithStages(messages,stage=response_checkpoint_level)  #give the stage argument to process up to the level
                    return jsonify(processed_messages)

                except Exception as e:
                    return jsonify("ProcessingError: %s",e)

                
            else:
                return jsonify("InputError: Unexpected Arguements")
        else:
            return jsonify("LOGIN REQUIRED")


    elif mthd == 'POST':
        try: 
            content_type = request.headers.get('Content-Type')
            data = request.get_json()
            rng = data['range']
            response_checkpoint_level=data['stage']
            st,et=rng[0],rng[1]
            host =  request.headers.get('Host')
            agent =  request.headers.get('User-Agent')
            current_app.logger.info('host: %s \n agent: %s \n',host,agent)
          


            try:
                e = GmailFetcher()
                messages = e.fetch(st,et)
                current_app.logger.info('msgs %s',e.qry)
                current_app.logger.info('msgs %s',len(messages))
                # rangeQuery = getQueryForDateRange(st,et)

            except Exception as e:
                current_app.logger.exception('WorkflowError: %s',e)
                return jsonify(e)

            if response_checkpoint_level==0:
                #returns without posting/saving anything.
                msgs = [m.__dict__ for m in messages]
                return jsonify(msgs)
            #goes on to extract data part
            # elif 0<response_checkpoint_level<=3:
            #     # try:
            #         current_app.logger.info('%s stage requested. Processing...',response_checkpoint_level)
            #         coded_content_json = extractCodedContentFromRawMessages(messages)
            #         current_app.logger.info('coded body extracted')
            #  ##INSERT PART STRT
            #         if coded_content_json:
            #             try:
            #                 response = InsertResponse()
            #                 with db.atomic():
            #                     for data_dict in coded_content_json:
            #                         try:
            #                             # print(data_dict)
            #                             res= RawTransactions.create(**data_dict)
            #                             res.save()
            #                             response.success_inserts.append(data_dict['msgId'])
            #                         except Exception as e:
            #                             current_app.logger.exception('Insert error in %s \n error: %s ',data_dict['msgId'],e)
            #                             response.failed_insert.append(data_dict['msgId'])
        
            #                     # res = Transactions.insert_many(data).execute()
                            
            #                 # print(type(res))
            #                 insert_response = {"status":True,
            #                                     "timespan":str(datetime.datetime.utcnow() - start_time),
            #                                     "success_inserts":response.success_inserts,
            #                                     "failed_inserts":response.failed_insert
            #                                     }
            #                 # return jsonify(insert_response)
            #                 current_app.logger.info('coded body Inserted')
            #             except Exception as e:
            #                 current_app.logger.exception('coded body Insert ERROR')
                    #     return jsonify(res)
            #         else:
            #             current_app.logger.info('No coded body ')
            #  ##INSERT PART DONE
                        
            #             # return jsonify('False')
            #         if response_checkpoint_level==1:
            #             return coded_content_json
            #         else:

            #             current_current_app.logger.info('decoding the coded body & extracting Transaction info')
            #             decoded_transaction_info = extractBodyFromEncodedData(coded_content_json) #big processing unit, split into chunks or make smaller
            #             current_app.logger.info('coded body extracted')
                        
            #          ##INSERT PART STRT
            #             try:
            #                 # current_app.logger.info('processing response for the stage %s',response_checkpoint_level)
                            
            #                 # processed_messages = processRawMessagesWithStages(messages,stage=response_checkpoint_level)  #give the stage argument to process up to the level
            #                 current_current_app.logger.info("Processed messages received")
            #                 def cleanTxnsBeforeInserting(decoded_transaction_info):
            #                     df = pd.DataFrame(decoded_transaction_info)
            #                     # print(df.head())
            #                     # print(meta)
            #                     df.dropna(subset=['msgId','amount_debited'],inplace=True)
            #                     df['amount_debited']= pd.to_numeric(df['amount_debited'], errors='coerce')
            #                     # df['date'] =pd.to_datetime(df['date'],format='%d-%m-%Y')
            #                     df['date'] = df['date'].apply(lambda x : datetime.strptime(x,'%d-%m-%y'))
            #                     df = df.convert_dtypes(infer_objects=True)
            #                     # print(df.dtypes)
            #                     meta = {"rows":df.shape[0],
            #                             "sum":sum(df['amount_debited'].to_list())}
            #                     # print(df.columns)
            #                     # print(meta)
            #                     data = df.to_dict(orient='records')
                                

            #                     return data
            #                 # try:
            #                 #     data = cleanTxnsBeforeInserting(decoded_transaction_info)
            #                 # except Exception as e:
            #                 #     current_current_app.logger.exception("Cleaning Error")
            #                 data = decoded_transaction_info
            #                 try:
            #                     if data:
            #                         response = InsertResponse()
            #                         with db.atomic():
            #                             for data_dict in data:
            #                                 try:
            #                                     # print(data_dict)
            #                                     res= Transactions.create(**data_dict)
            #                                     res.save()
            #                                     response.success_inserts.append(data_dict['msgId'])
            #                                 except Exception as e:
            #                                     current_app.logger.exception('Insert error in %s \n error: %s ',data_dict['msgId'],e)
            #                                     response.failed_insert.append(data_dict['msgId'])
                
            #                             # res = Transactions.insert_many(data).execute()
                                    
            #                         # print(type(res))
            #                         insert_response = {"status":True,
            #                                             "timespan":str(datetime.datetime.utcnow() - start_time),
            #                                             "success_inserts":response.success_inserts,
            #                                             "failed_inserts":response.failed_insert
            #                                             }
            #                         return jsonify(insert_response)
            #                     #     return jsonify(res)
            #                     else:
            #                         return jsonify('no data returned from cleaning')
            #                 except Exception as e:
            #                     return  jsonify("DBInsertError: %s",e)

            #             except Exception as e:
            #                 return jsonify("ProcessingError: %s",e)
                        
            #             if response_checkpoint_level>=2:
            #                 return decoded_transaction_info
            else:
                pass  #to next try/catch
            
            

        except Exception as e:

            return jsonify("UnidentifiedError:",e)
        # except Exception as e:
        #     return jsonify("TypeError: Content-Type not supported!")