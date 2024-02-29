
import datetime
import uuid

def get_now_time_string():

    end_time = datetime.datetime.utcnow().replace(tzinfo=None)
    return end_time.__str__()


def get_random_execution_id():
    """Generates a random, lightweight execution ID using UUID."""
    return str(uuid.uuid4())[:8]  # Use the first 8 characters for brevity