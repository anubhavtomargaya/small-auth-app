# from _typeshed.wsgi import WSGIEnvironment
from flask import Flask, render_template, jsonify, request,make_response
# from authlib.integrations.flask_client import OAuth
from flask_cors import CORS,cross_origin
# from app import app
import requests
from workflow import *
from wf_decode import decode
from gmail_fetcher import GmailFetcher,GmailQuery

from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GReq
from models import *
from peewee import IntegrityError

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from flask import Request
import auth as google_auth
import logging
# logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)
# app.config['SERVER_NAME'] = 'localhost:5000'
# oauth = OAuth(app)
app = Flask(__name__)
CORS(app)

app.secret_key = "MYSK3Y"
# os.environ.get("FN_FLASK_SECRET_KEY", default=False)

app.register_blueprint(google_auth.app)

 
@app.route('/index',methods=['GET'])
def index():
    todo = {
            "todo":
                [
                    {
                        1: "fetch emails for key 'today' like lastday",
                        2: "handle the integrity error for inserts",
                        3: "run scheduler at 4am to pull data till 4 of the day",
                        4: "make a contract for both endpoints' req-res"
                    }        
                ],
            "completed": {0:"pulling data from gmail & decoding as a service,",
                            1:"process transaction info to filter only insights dimensions and remove meta dimensions",

            }
            }
    # return jsonify({'hi'})
    return render_template("index.html")

class FetchRequest:
    def __init__(self,req:Request) -> None:
   
        body = req.json
        range = req.args.get('range') #
        stage = req.args.get('stage')
        data = req.get_json()
        rng = data['range']
        st,et=rng[0],rng[1]

    def getHeader(self):pass



##google login
@app.route('/',methods=['GET','POST'])
def login():
    d=request.data
    app.logger.info('body: %s',d)
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        creds = google_auth.build_credentials()
        app.logger.info(d)
        return '<div>You are logged in! <div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
        # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
    else:
        return render_template("index.html")
    # 'You are not currently logged in.'
    # return jsonify({'hi'})

@app.route('/fetch',methods=['GET'])
def fetch():
    if google_auth.is_logged_in():
        # user_info = google_auth.get_user_info()
        st = request.args.get('start_')
        et = request.args.get('end_')
        current_app.logger.info("st et %s %s ",st,et)
        if not st or not et:
            st = '2023-11-01'
            et = '2023-11-10'
        creds = google_auth.build_credentials()
        current_app.logger.info("creds",creds)
        q = GmailQuery(st,et,from_='alerts@hdfcbank.net')
        e = GmailFetcher()
        e.gmail_service = build('gmail', 'v1', credentials=creds)
        current_app.logger.info("service: %s" , e.gmail_service)
        threads = google_auth.get_matched_emails(q)
        messages = e.fetch(st,et)
        # current_app.logger.info('msgs %s',e.qry)
        current_app.logger.info('TYPE %s',type(threads))
        current_app.logger.info('obj %s',threads)
        # current_app.logger.info('red %s',creds.refresh(GReq()))
        current_app.logger.info('threads %s',len(threads))
        current_app.logger.info('msgs %s',len(messages))
        list_of_dicts = [{attr: getattr(obj, attr) for attr in vars(obj)} for obj in messages]
        list_of_smaller_dicts = extractCodedContentFromRawMessages(list_of_dicts)
        list_of_content_dicts = extractBodyFromEncodedData(list_of_smaller_dicts)
        return '<div>your creds <div><pre> ' + json.dumps(list_of_content_dicts, indent=4) + "</pre>"
        # return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
    else:
        return render_template("index.html")
    # 'You are not currently logged in.'
    # return jsonify({'hi'})


##google login end

class FetchGetRequest:
    def __init__(self,request:Request) -> None:
        self.range_str = request.args.get('range_str')
        self.stage = request.args.get('stage')
        self.mthd = request.method 



@app.route('/api/v1/fetch/',methods=['GET','POST'])
def fetchTransactionEmailsFromGmail():
    start_time = datetime.datetime.utcnow()
    mthd = request.method 
    args = request.args
    
    # if (content_type == 'application/json'):
    # data = request.data

    app.logger.info('query: %s',mthd)
    # return jsonify(mthd)
    
    # else:
        # return "TypeError: Content-Type not supported!"
    # body = request.get_json()
    
    # app.logger('request received: %s \n %s \n %s',mthd,body,data)
    if mthd == 'GET':
        app.logger.info('args: %s',args)
        ###read arguements
        if args.get('range_str'):
            query_range_str = args.get('range_str') #1
        else:

            return jsonify("MissingArgument: Arguements 'range' missing")

        if args.get('stage'):
            response_checkpoint_level = int(args.get('stage')) #2
            app.logger.info('setting response stage from stage argument as %s',response_checkpoint_level)
        else:
            response_checkpoint_level=0
            app.logger.info('setting response stage as 0, i.e: RAW')
        
        ###fetch messages for range param from gmail & return based on requested stage
        if query_range_str=='lastday':
            try:
                lastDayQuery = getQueryForLastDay()
                app.logger.info('query: %s',lastDayQuery)
                messages = fetchRawMessagesForQuery(lastDayQuery) 
                app.logger.info('msgs: %s',type(messages))
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
                app.logger.info('processing response for the stage %s',response_checkpoint_level)
                processed_messages = processRawMessagesWithStages(messages,stage=response_checkpoint_level)  #give the stage argument to process up to the level
                return jsonify(processed_messages)

            except Exception as e:
                return jsonify("ProcessingError: %s",e)

            
        else:
            return jsonify("InputError: Unexpected Arguements")


    elif mthd == 'POST':
        try: 
            content_type = request.headers.get('Content-Type')
            data = request.get_json()
            rng = data['range']
            response_checkpoint_level=data['stage']
            st,et=rng[0],rng[1]
            host =  request.headers.get('Host')
            agent =  request.headers.get('User-Agent')
            app.logger.info('host: %s \n agent: %s \n',host,agent)
          


            try:
                e = GmailFetcher()
                messages = e.fetch(st,et)
                current_app.logger.info('msgs %s',e.qry)
                current_app.logger.info('msgs %s',len(messages))
                # rangeQuery = getQueryForDateRange(st,et)

                # app.logger.info('query: %s',rangeQuery)

                # messages = fetchRawMessagesForQuery(rangeQuery) 
                # raw_file_name = f"RAW - {str(datetime.datetime.now())}_.json"
                # #  #token will go here
                # current_app.logger.info('Saving RAW MESSAGES')
                # with open(raw_file_name, 'w') as f:
                #     json.dump(messages,f)
                # current_app.logger.info('.........SAVED')

            except Exception as e:
                logger.exception('WorkflowError: %s',e)
                return jsonify(e)

            if response_checkpoint_level==0:
                #returns without posting/saving anything.
                msgs = [m.__dict__ for m in messages]
                return jsonify(msgs)
            #goes on to extract data part
            # elif 0<response_checkpoint_level<=3:
            #     # try:
            #         app.logger.info('%s stage requested. Processing...',response_checkpoint_level)
            #         coded_content_json = extractCodedContentFromRawMessages(messages)
            #         app.logger.info('coded body extracted')
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
            #                             app.logger.exception('Insert error in %s \n error: %s ',data_dict['msgId'],e)
            #                             response.failed_insert.append(data_dict['msgId'])
        
            #                     # res = Transactions.insert_many(data).execute()
                            
            #                 # print(type(res))
            #                 insert_response = {"status":True,
            #                                     "timespan":str(datetime.datetime.utcnow() - start_time),
            #                                     "success_inserts":response.success_inserts,
            #                                     "failed_inserts":response.failed_insert
            #                                     }
            #                 # return jsonify(insert_response)
            #                 app.logger.info('coded body Inserted')
            #             except Exception as e:
            #                 app.logger.exception('coded body Insert ERROR')
                    #     return jsonify(res)
            #         else:
            #             app.logger.info('No coded body ')
            #  ##INSERT PART DONE
                        
            #             # return jsonify('False')
            #         if response_checkpoint_level==1:
            #             return coded_content_json
            #         else:

            #             current_app.logger.info('decoding the coded body & extracting Transaction info')
            #             decoded_transaction_info = extractBodyFromEncodedData(coded_content_json) #big processing unit, split into chunks or make smaller
            #             app.logger.info('coded body extracted')
                        
            #          ##INSERT PART STRT
            #             try:
            #                 # app.logger.info('processing response for the stage %s',response_checkpoint_level)
                            
            #                 # processed_messages = processRawMessagesWithStages(messages,stage=response_checkpoint_level)  #give the stage argument to process up to the level
            #                 current_app.logger.info("Processed messages received")
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
            #                 #     current_app.logger.exception("Cleaning Error")
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
            #                                     app.logger.exception('Insert error in %s \n error: %s ',data_dict['msgId'],e)
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

        
@app.route('/api/v1/getEmailBody/',methods=['GET'])
def getEmailsBody():
    mthd = request.method 
    hdrs = request.headers
    data = request.json

    if mthd == 'GET':
        body = getEmailBody(data[0]['codata'])
        return jsonify(body)
        # app.logger.info('args: %s',args)
        ###read arguements
        # if args.get('range'):
        #     query_range_str = args.get('range') #1
        # else:

        #     return jsonify("MissingArgument: Arguements 'range' missing")


@app.route('/api/v1/decode/',methods=['POST'])
def decodeGmailResponse():
    # current_app.logger.info('req, %s',request)
    mthd = request.method 
    content_type = request.headers.get('Content-Type')
    userid = request.headers.get('userid')

    if (content_type == 'application/json'):
        body = request.get_json()

    else:
        return "TypeError: Content-Type not supported!"
    # current_app.logger.info('body:%s',body)


    if mthd == 'POST' and body:
        try:
            current_app.logger.info('decoding & extracting transaction details: %s' ,type(body))
            #wf_decode returns list of decoded txns
            decoded_transaction_info = decode(body)
            res = [tx.__dict__ for tx in decoded_transaction_info]
            return jsonify(res)
        except Exception as e:
            current_app.logger.exception("exception")
            return ("DecodingError %s",e)
    else:
        return "InvalidRequest"



# @app.route('/api/v1/decode/',methods=['POST'])
# def extractTransactionFromCodedMessages():
#     mthd = request.method 
#     hdrs = request.headers
#     content_type = request.headers.get('Content-Type')
#     if (content_type == 'application/json'):
#         body = request.get_json()

#     else:
#         return "TypeError: Content-Type not supported!"
#     body = request.get_json()
#     # if isinstance(body,str):
#     #     body=json.dumps(request.data)

#     if mthd == 'POST' and body:
        
#         try:
#             logger.info('decoding & extracting transaction details' )
#             decoded_transaction_info = extractBodyFromEncodedData(body)
#             return decoded_transaction_info
#         except Exception as e:
#             app.logger.info(body)
#             return ("DecodingError %s",e)
#     else:
#         return "InvalidRequest"
 

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0',port=5000,debug=True)
    # app.run(debug=True)