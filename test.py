"""
get stage 1 response for last day and send it to
decode endpoint to get the stage 2 transacion info
"""
import pandas as pd

from datetime import datetime
import json
import requests
from flask import jsonify
from playhouse.shortcuts import model_to_dict  

from src.models import Transactions,db
# from src.test import db
fetchbaseurlget = 'http://localhost:105/api/v1/fetch/?range=lastday&stage=1'
fetchbaseurlpost = 'http://localhost:105/api/v1/fetch/'

# headers = {"Content-Type":'application/json'}

# # res = requests.get(fetchbaseurlget)
# # coded_response =(res.json())
# # print(res.json())
# d ={  "range":['2023-03-01','2023-03-03'],"stage":3 }
# # print(headers)
# res_post = requests.post(fetchbaseurlpost,headers=headers,
#                                         json=d
#                                             )
# txn_res =(res_post.json())
# print((txn_res))
# df = pd.DataFrame(txn_res)
# meta = {"rows":df.shape[0],
#         "sum":sum(pd.to_numeric(df['amount_debited'],errors='coerce').to_list())}
# # print(df.head())
# # print(meta)
# df.dropna(subset=['msgId','amount_debited'],inplace=True)
# df['amount_debited']= pd.to_numeric(df['amount_debited'], errors='coerce')
# # df['date'] =pd.to_datetime(df['date'],format='%d-%m-%Y')
# df['date'] = df['date'].apply(lambda x : datetime.strptime(x,'%d-%m-%y'))
# df = df.convert_dtypes(infer_objects=True)
# # print(df.dtypes)
# meta = {"rows":df.shape[0],
#         "sum":sum(df['amount_debited'].to_list())}
# # print(df.columns)
# # print(meta)
# data = df.to_dict(orient='records')
# # print(data)

# # print(txn_res[0])
# with db.atomic():
#     res = Transactions.insert_many(df.to_dict(orient='records')).execute()

# print(type(res))

query = Transactions.select()
output = []
for row in query:
    output.append(model_to_dict(row))
# print(output)
df = pd.DataFrame(output)
print(df['msgId'].nunique())


# print(coded_response)
# filter_keys =  ['msgEpochTime','threadId','msgId','msgEncodedData']
# post_body = [{k:v for y in if i} for i in coded_response]


# decodebaseurlpost = 'http://localhost:105/api/v1/decode/'
# post_res = requests.post(url=decodebaseurlpost,headers=headers, json=coded_response)
# print(post_res.json())
# old_keys = ['msgEpochTime','threadId','msgId','msgEncodedData']
# returns= ['oldkeys','amount_debited','to_vpa','date'] #removes msgEncodedData