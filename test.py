"""
get stage 1 response for last day and send it to
decode endpoint to get the stage 2 transacion info
"""

import json
import requests
from flask import jsonify
baseurlget = 'http://localhost:105/api/v1/fetch/?range=lastday&stage=1'
res = requests.get(baseurlget)
coded_response =(res.json())
# print(res.json())

# print(coded_response)
# filter_keys =  ['msgEpochTime','threadId','msgId','msgEncodedData']
# post_body = [{k:v for y in if i} for i in coded_response]

headers = {"Content-Type":'application/json'}
baseurlpost = 'http://localhost:105/api/v1/decode/'

post_res = requests.post(url=baseurlpost,headers=headers, json=coded_response)
print(post_res.json())
old_keys = ['msgEpochTime','threadId','msgId','msgEncodedData']
returns= ['oldkeys','amount_debited','to_vpa','date'] #removes msgEncodedData