from peewee import *
import logging

from config import username,password,database_name,endpoint

# db= MySQLDatabase(database_name,username ,password,endpoint)
db = SqliteDatabase(':memory:')
curs = db.cursor()

##models

class BaseModel(Model):
    class Meta:
        database = db

class Transactions(BaseModel):
    txn_id = AutoField() #change to the upstream txn primary key 
    date_of_txn = DateField() #give format according to upstream
    sent_to = TextField(225)
    amount_debited = DecimalField(8)
    timestamp = TimestampField()
    additional_category_1 = TextField(default=None)
    additional_category_2 = TextField(default=None)

    class Meta:
        table_name = 'transactions_01'

# db.create_tables([Transactions])
