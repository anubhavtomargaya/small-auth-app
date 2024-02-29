
from src.common.common_utils import get_now_time_string
from src.common.db_init import Transactions, db,PipelineExecutionMeta,RawTransactions
from playhouse.shortcuts import model_to_dict
tables_in_db = [PipelineExecutionMeta,RawTransactions]
if __name__ == '__main__':

    # db.create_tables(tables_in_db)
    # print(db.get_tables())
    # print(db.drop_tables(tables_in_db))
    # print(db.get_tables())
    # query = PipelineExecutionMeta.select()
    # # query = RawTransactions.select()
    id_list =  [
      "18deb2ba3bf25489",
      "18de145e308afb42",
      "18ddab43af8bc04d",
      "18ddad35b8fba310",
      "18dd46006477cfd8",
      "18dd4f33636fdff3",]
    # query = RawTransactions.select().where(RawTransactions.msgId << id_list)
    # for transaction in query:
    #     print( transaction.snippet )

    query = Transactions.select().where(Transactions.msgId << id_list)
    for transaction in query:
        print( model_to_dict(transaction) )
    # output = []
    # for row in query:
    #     output.append(model_to_dict(row))
    # print(len(output))
    # print(output)
    # print(get_now_time_string())