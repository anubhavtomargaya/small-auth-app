from peewee import *
import logging
from playhouse.shortcuts import model_to_dict  
# from config import username,password,database_name,endpoint
endpoint = "mgdb.cvatnnmljapj.ap-southeast-1.rds.amazonaws.com"
username = "gandhi"
password = "moneyman"
database_name = "SPDB"


# db= MySQLDatabase(database_name,username ,password,endpoint)
# db = SqliteDatabase(':memory:')
db = PostgresqlDatabase('SPDB',host= endpoint, 
                            user=username,password = password,port=5432)

# print(db.get_tables())
# curs = db.cursor()

##models

class BaseModel(Model):
    class Meta:
        database = db

class Transactions(BaseModel):
    txn_id = AutoField() #change to the upstream txn primary key 
    msgId=TextField(unique=True)
    msgEpochTime = BigIntegerField()
    date = DateField(formats=['%d-%m-%Y','%Y-%m-%d']) #give format according to upstream
    to_vpa = TextField(225)
    amount_debited = DecimalField()
    additional_category_1 = TextField(null=True, default=None)
    additional_category_2 = TextField(null=True,default=None)

    class Meta:
        table_name = 'transactions_02'

class VPA(BaseModel):
    id = AutoField() #change to the upstream txn primary key 
    vpa_user=TextField(unique=True)
    vpa_provider = TextField()
    category =  TextField(null=True)
    additional_category_1 = TextField(null=True, default=None)
    additional_category_2 = TextField(null=True,default=None)

    class Meta:
        table_name = 'vpa'


class InsertResponse():
    
    def __init__(self) -> None:
        self.success_inserts = []
        self.failed_insert = []


# db.create_tables([VPA])
# print(db.get_tables())
# print(db.drop_tables([Transactions]))
# print(db.get_tables())
# query = Transactions.select()
# output = []
# for row in query:
#     output.append(model_to_dict(row))
# print(output)



