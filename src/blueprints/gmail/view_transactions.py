

from src.common.db_init import Transactions,db
from peewee import fn
from playhouse.shortcuts import model_to_dict

class TransactionDims:
    def __init__(self,
                 new:bool=True,
                 include_in_agg:bool=True,
                 labelled:bool=None,
               ) -> None:
        # self.new = new #updated when after the load user saves the transaction to False, or when cookies cleared
        self.labelled = labelled #updated True when user gives some input to tag/label, else update to false in exiting session, None when init
        self.include_in_agg =include_in_agg # tags like self, credit card bills etc can be excluded from aggregates in reports

class TransactionUpdates:
    def __init__(self,
                 updated_amount:int=None,
                 label:str=None,
                 split_by:int=None) -> None:
        self.updated_amount = updated_amount 
        self.label = label 
        self.split_by = split_by

class TransactionRequest:
    def __init__(self,
                 start,
                 end,) -> None:
        pass

from datetime import datetime,timedelta

def _query_transaction_table_by_range(start,end):
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d').date()
        end_date = datetime.strptime(end, '%Y-%m-%d').date() + timedelta(days=1)  # Include end date
        #need to add user id to table
        query = Transactions.select(Transactions.msgId,Transactions.msgEpochTime,Transactions.date,Transactions.to_vpa,Transactions.amount_debited).where(
        (Transactions.date >= start_date) & (Transactions.date < end_date)
        )
        # query = Transactions.select().where(Transactions.date > start )
        output = list(query.execute())
        return output
    except Exception as e:
        raise e
    
def _prepare_txn_for_show(txn_models:list):
    """ if need to return a proper view from backend how should the final schema look.
            - column names (case sensitive)
            - no meta columns (remove ids)
            - ordered by time desc 
            - date time in str format, timezone IST
            - currency info added, formatted
        """

    tmp_df = pd.DataFrame([ model_to_dict( model,exclude=[Transactions.txn_id,Transactions.record_created_at])
                            for model in txn_models],
                        ).set_index('msgId',drop=True)
    
    tmp_df[['merchant','bank']] = tmp_df['to_vpa'].str.split('@',expand=True)
    # drop unnecessary -> bank, msgId,to_vpa,
    # rename cols -> rcvd_time, Merchant/POS, Amount, Date
    # format dttm -> msgEpochTime
    # dw about currency for now
    # order by time and return
    # reset index (0...9)
    return tmp_df

    
class TraxModel:
    def __init__(self,
                 ) -> None:
        pass

import pandas as pd
def get_transactions_view(start,
                          end,
                          exec_session_id=None,
                          df=True,
                          records=False)->pd.DataFrame:
    """ if session_id is passed, assume that caller service is calling after the load.
        query the txn table by session id (once the column is added it can be tested)
        instead of by_range, by_session_id will be introduced and used.

        """
    txn_models = _query_transaction_table_by_range(start,end)
    tmp_df = _prepare_txn_for_show(txn_models)
    if df:
        return tmp_df
    if not df:
        return tmp_df.to_dict(orient="records")
    if records:
        return tmp_df.to_records(),list(tmp_df.columns)
        # my_list = [ model_to_dict( model,exclude=[Transactions.txn_id,Transactions.record_created_at]) for model in txn_models]
        # return [v['merchant']==str(v['to_vpa']).split('@')[0] for v in my_list]


# query = "SELECT * FROM upi_transactions WHERE strftime('%Y-%m-%d', datetime(msgEpochTime, 'unixepoch')) BETWEEN '2024-02-24' AND '2024-02-29' "
# cursor = db.execute(query)
# transactions = list(cursor.fetchall())
# for txn in transactions:
start ='2024-02-01'
end ='2024-02-04'
print(get_transactions_view(start=start,
                            end=end,
                            df=False))
#   print(txn.txn_id, txn.msgId, txn.date)

## case I - after the load, the caller service uses the returned exec_session_id to fetch the records 
#        from upi_transactions table inserted latest. when this happens if other transactions are also to be 
#       loaded at in the same vieweing session it can do so by calling the same api but additional bool labelled=False
## CASE II - more general, whenever the records are queried to show the  user start / end dates are passed
#   above this the records can be joined and filtered based on many dimensions
#       basic - all txns in table format: query > beautify > show 
#       filter - exlude_agg : query > filter by dim of name > beautify > show