from peewee import *

from peewee import *
import logging
from workflow import getEmailBody
from config import username,password,database_name,endpoint

# db= MySQLDatabase(database_name,username ,password,endpoint)
# db = SqliteDatabase(':memory:')
# db = PostgresqlDatabase('SPDB',host= endpoint, 
#                             user=username,password = password,port=5432)

# print(db.get_tables())

from workflow import GmailConnector,buildGmailService

# gm = GmailConnector()
# gm.buildService()
sr = buildGmailService()
print(sr)