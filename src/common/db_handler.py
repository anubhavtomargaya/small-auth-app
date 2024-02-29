from src.common.db_init import PipelineExecutionMeta, RawTransactions,db
from src.common.models import MetaEntry

from peewee import IntegrityError
def insert_raw_transaction(data):
    """Inserts a single raw transaction into the database.

    Args:
        data (dict): Dictionary containing raw transaction data.

    Returns:
        RawTransactions: The created RawTransactions object.
    """
    try:
        return RawTransactions.create(**data)
    except Exception as e:
        raise Exception('Error inserting RawTransaction: %s', e)
     

def insert_raw_transactions(data_list):
    """Inserts multiple raw transactions into the database.

    Args:
        data_list (list): List of dictionaries containing raw transaction data.

    Returns:
        list: List of created RawTransactions objects.
    """
    print("data list",data_list)
    # created_objects = []
    inserted_objects = []
    existing_ids = []
    for row_data in data_list:
        try:
                
            with db.atomic():
                    # Attempt insert using insert_many with ignore conflicts
                    # inserted_objects.extend(RawTransactions.insert_many(row_data).execute())
                    inserted_object = RawTransactions.insert_many(row_data).execute()
                    inserted_objects.append(inserted_object)
            # created_objects.append(insert_raw_transaction(row_data))
        except IntegrityError as e:
            # Extract existing message IDs from the error message
            if 'UNIQUE constraint failed: raw_transactions.msgId' in str(e):
                existing_ids.append(row_data['msgId'])  # Assuming 'msgId' is the unique field
            else:
                raise e  # Re-raise other exceptions

    return existing_ids, inserted_objects

def insert_many_raw_transactions(data_list):
    """Inserts multiple raw transactions into the database efficiently.

    Args:
        data_list (list): List of dictionaries containing raw transaction data.

    Returns:
        int: The number of rows inserted.
    """
    try:
        # Perform bulk insert using insert_many
        with db.atomic():  # Ensure transaction safety
            inserted_count = RawTransactions.insert_many(data_list).execute()
        return inserted_count
    except Exception as e:
        raise Exception('Error inserting RawTransactions: %s', e)
   

def insert_execution_metadata(meta:MetaEntry):
    try:
        
        PipelineExecutionMeta.create(
            execution_id=meta.execution_id,
            gmail_query=meta.query,
            start_time=meta.start_time,
            end_time=meta.end_time,
            thread_count=meta.thread_count,
            email_message_count=meta.email_message_count,
            raw_message_count=meta.raw_message_count,
            decoded_message_count=meta.decoded_message_count,
            status=meta.status,
            user_id = 'me'
        )
        print("inserted metadata entry: ", meta.execution_id)
    except Exception as e:
        raise Exception(f"Unable to insert entry: {e}")


def update_stage_data(execution_id, stage_name, **kwargs):
    """Creates a new PipelineStage entry for the given execution and stage."""

    # Extract additional data from kwargs (if relevant)
    thread_count = kwargs.get("thread_count", 0)
    email_message_count = kwargs.get("email_message_count", 0)
    raw_message_count = kwargs.get("raw_message_count", 0)
    decoded_message_count = kwargs.get("decoded_message_count", 0)

    # Create a new stage entry
    PipelineExecutionMeta.create(
        execution_meta_id=execution_id,
        stage_name=stage_name,
        thread_count=thread_count,
        email_message_count=email_message_count,
        raw_message_count=raw_message_count,
        decoded_message_count=decoded_message_count,
    )
