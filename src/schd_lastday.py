import pandas as pd

from datetime import datetime
import json
import requests
# from flask import jsonify
# from playhouse.shortcuts import model_to_dict  
import logging 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
from models import InsertResponse, Transactions,db

def main():
    try:
# from src.test import db
        fetchbaseurlget = 'http://localhost:5000/api/v1/fetch/?range=lastday&stage=3'
        # fetchbaseurlpost = 'http://localhost:105/api/v1/fetch/'
        start_time = datetime.utcnow()
        headers = {"Content-Type":'application/json'}

        res = requests.get(fetchbaseurlget)
        txn_res =res.json()
        print(res.json())
        # d ={  "range":['2023-03-01','2023-03-03'],"stage":3 }
        # print(headers)
        # res_post = requests.post(fetchbaseurlpost,headers=headers,
        #                                         json=d
        #                                             )
        # txn_res =(res_post.json())
        df = pd.DataFrame(txn_res)
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
                        print(data_dict)
                        res= Transactions.create(**data_dict)
                        res.save()
                        response.success_inserts.append(data_dict['msgId'])
                    except Exception as e:
                        logger.exception('Insert error in %s \n error: %s ',data_dict['msgId'],e)
                        response.failed_insert.append(data_dict['msgId'])

                # res = Transactions.insert_many(data).execute()
            
            # print(type(res))
            insert_response = {"status":True,
                                "timespan":str(datetime.utcnow() - start_time),
                                "success_inserts":response.success_inserts,
                                "failed_inserts":response.failed_insert
                                }
            print(insert_response)
            logger.info(insert_response)
        #   return jsonify(res)
            return True
        else:
            print(False)
            logger.info('False')
            return False

    except Exception as e:
        print(e)
        return e

print(main())