from flask import Flask, render_template, jsonify, request,make_response
# from authlib.integrations.flask_client import OAuth
from flask_cors import CORS,cross_origin
# from app import app
import requests
from workflow import *
app = Flask(__name__)
CORS(app)
import logging
# logging.basicConfig(level=logging.INFO)
logger= logging.getLogger(__name__)
# app.config['SERVER_NAME'] = 'localhost:5000'
# oauth = OAuth(app)
 
@app.route('/',methods=['GET'])
def index():
    todo = {
            "todo":
                [
                    {
                        1: "fetch emails for key 'today' like lastday",
                        2: "process transaction info to filter only insights dimensions and remove meta dimensions",
                        3: "make a contract for both endpoints' req-res"
                    }        
                ],
            "completed": "pulling data from gmail & decoding as a service,"

            }
    # return jsonify({'hi'})
    return jsonify(todo)





@app.route('/api/v1/fetch/',methods=['GET','POST'])
def fetchTransactionEmailsFromGmail():
    mthd = request.method 
    args = request.args
    body = request.data

    app.logger.info('args: %s',args)
    if mthd == 'GET':
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
        return jsonify(args)
 


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
    app.run(host='0.0.0.0',port=105,debug=True)
    # app.run(debug=True)