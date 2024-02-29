
from src.common.common_utils import get_now_time_string
from src.common.db_init import db,PipelineExecutionMeta,RawTransactions
from playhouse.shortcuts import model_to_dict
tables_in_db = [PipelineExecutionMeta,RawTransactions]
if __name__ == '__main__':

    # db.create_tables(tables_in_db)
    # print(db.get_tables())
    # print(db.drop_tables(tables_in_db))
    print(db.get_tables())
    query = PipelineExecutionMeta.select()
    # query = RawTransactions.select()
    output = []
    for row in query:
        output.append(model_to_dict(row))
    print(len(output))
    print(output)
    # print(get_now_time_string())