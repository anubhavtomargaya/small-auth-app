
# query = RawTransactions.select().where(RawTransactions.msgId << id_list)
# for transaction in query:
#     print( transaction.snippet )

from src.blueprints.gmail.store import vpa_store
from src.blueprints.gmail import store

from src.common.db_init import Transactions
from playhouse.shortcuts import model_to_dict

def aztec():
    
   pass 

def ass_tag(userid,sessionid=None):
    #
    # get transaction from session id
    # find if vpa exists with tag/label
    # add suggested tag if does
    # group transactions of user based on time & amount
    # find if any transaction falling in labelled group
    pass

def _get_txns(msgId:list):
    if not isinstance(msgId,list):
        raise TypeError("Pass a list of msgIds")
    query = Transactions.select().where(Transactions.msgId << msgId)
    output = [tx for tx in query]
    # for transaction in query:
    return output
        # print( transaction.snippet )

def _process_vpa(vpa:str):
    merchant,bank = vpa.split('@')
    # print(vpa_store)
    m = fuzzy_match_merchant(merchant, store.char_store)
    print(m)
    print("MER")
    # # if merchant in store.char_store:
    #     print('True',merchant,store.char_store[merchant])

    # else:
    #     print("NOT TRUE",merchant)

from fuzzywuzzy import process

def fuzzy_match_merchant(vpa, char_store:dict):
  """
  Performs a fuzzy match on the merchant names in the 'char_store' dictionary.

  Args:
      vpa (str): The VPA to search for a match.
      store (object): An object containing the 'char_store' dictionary.

  Returns:
      str: The best matching merchant name from the dictionary (or None if no match).
  """
  # Set a threshold for similarity score (adjust based on your needs)
  threshold = 80

  # Get all possible matches with a score above the threshold
  matches = process.extract(vpa, char_store.keys(), limit=1)

  # Return the first match if it exists, otherwise None
  if matches:
    return matches  # Return the matched key (merchant name)
  else:
    return None


if __name__ == '__main__':
    msgid = ['18dc7a8270c70049',
             '18dc7c057e8934d6',
             '18d1ccf5cc2a5999',
             '18d40e5e0e9d6e91']
    txns = _get_txns(msgid)
    for i in txns:
        print(i.to_vpa)
        _process_vpa(i.to_vpa)
    # print(store.char_store.keys())
    #         # Example usage
    # vpa = "swiggy"  # New VPA to search for
    # matched_merchant = fuzzy_match_merchant(vpa, store.char_store)

    # if matched_merchant:
    #     print(f"Matched merchant: {matched_merchant}")
    #     print(f"Category: {store.char_store[matched_merchant]}")
    # else:
    #     print("No close match found for the VPA")
    