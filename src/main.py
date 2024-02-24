from flask import Flask, render_template, jsonify, request,make_response
# from authlib.integrations.flask_client import OAuth
from flask_cors import CORS,cross_origin
# from app import app
import requests
from workflow import *
from models import *
from peewee import IntegrityError

from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

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
    return jsonify(todo)




##google login
@app.route('/',methods=['GET'])
def login():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        return '<div>You are currently logged in as ' + user_info['given_name'] + '<div><pre>' + json.dumps(user_info, indent=4) + "</pre>"
    else:
        return 'You are not currently logged in.'
    # return jsonify({'hi'})


##google login end



@app.route('/api/v1/fetch/',methods=['GET','POST'])
def fetchTransactionEmailsFromGmail():
    start_time = datetime.utcnow()
    mthd = request.method 
    args = request.args
    # if (content_type == 'application/json'):
    # data = request.data
    
    # else:
        # return "TypeError: Content-Type not supported!"
    # body = request.get_json()
    
    # app.logger('request received: %s \n %s \n %s',mthd,body,data)
    if mthd == 'GET':
        app.logger.info('args: %s',args)
        ###read arguements
        if args.get('range'):
            query_range_str = args.get('range') #1
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

            except Exception as e:
                logger.exception('WorkflowError: %s',e)

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
            # host =  request.headers.get('authtoken') #take auth token at runtime and call the service with this token
            agent =  request.headers.get('User-Agent')
            app.logger.info('host: %s \n agent: %s \n',host,agent)
            try:
                rangeQuery = getQueryForDateRange(st,et)

                app.logger.info('query: %s',rangeQuery)

                messages = fetchRawMessagesForQuery(rangeQuery)  #token will go here

            except Exception as e:
                logger.exception('WorkflowError: %s',e)
                return jsonify(e)

            if response_checkpoint_level==0:
                return jsonify(messages)
            else:
                pass  #to next try/catch
            
            try:
                app.logger.info('processing response for the stage %s',response_checkpoint_level)
                processed_messages = processRawMessagesWithStages(messages,stage=response_checkpoint_level)  #give the stage argument to process up to the level
                # app.logger.info(type(processed_messages))
                try:
                    df = pd.DataFrame(processed_messages)
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
                    
                    
                    if data:
                        response = InsertResponse()
                        with db.atomic():
                            for data_dict in data:
                                try:
                                    # print(data_dict)
                                    res= Transactions.create(**data_dict)
                                    res.save()
                                    response.success_inserts.append(data_dict['msgId'])
                                except Exception as e:
                                    app.logger.exception('Insert error in %s \n error: %s ',data_dict['msgId'],e)
                                    response.failed_insert.append(data_dict['msgId'])
    
                            # res = Transactions.insert_many(data).execute()
                        
                        # print(type(res))
                        insert_response = {"status":True,
                                            "timespan":str(datetime.utcnow() - start_time),
                                            "success_inserts":response.success_inserts,
                                            "failed_inserts":response.failed_insert
                                            }
                        return jsonify(insert_response)
                    #     return jsonify(res)
                    else:
                        return jsonify('False')
                except Exception as e:
                    return  jsonify("DBInsertError: %s",e)

            except Exception as e:
                return jsonify("ProcessingError: %s",e)

        except Exception as e:
            return jsonify(e)
        # except Exception as e:
        #     return jsonify("TypeError: Content-Type not supported!")

        
 


@app.route('/api/v1/decode/',methods=['POST'])
def extractTransactionFromCodedMessages():
    mthd = request.method 
    hdrs = request.headers
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        body = request.get_json()

    else:
        return "TypeError: Content-Type not supported!"
    body = request.get_json()
    # if isinstance(body,str):
    #     body=json.dumps(request.data)

    if mthd == 'POST' and body:
        
        try:
            logger.info('decoding & extracting transaction details' )
            decoded_transaction_info = extractBodyFromEncodedData(body)
            return decoded_transaction_info
        except Exception as e:
            app.logger.info(body)
            return ("DecodingError %s",e)
    else:
        return "InvalidRequest"
 

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host='0.0.0.0',port=5000,debug=True)
    # app.run(debug=True)