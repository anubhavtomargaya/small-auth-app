import peewee

from src.common.db_init import Transactions


class LabelVPARequest:
    def __init__(self,
                 msgId:str,
                 vpa:str,
                 input_label:str,
                 apply_to_all:bool=True, #by default update all vpa with the label
                 ) -> None:
        
        self.msgId = msgId
        self.vpa = vpa
        self.input_label = input_label
        self.apply_to_all=apply_to_all

class LabelConfigRequest:
    def __init__(self,
                 execution_id:str,
                 ) -> None:
        
        self.execution_id = execution_id

def update_label_from_config(request: LabelConfigRequest):
    """Updates the label of new transactions based on historical default labels for the same VPAs.
        in the latest load session update the loaded vpas based on the historical
        transactions. If the loaded VPAs are present in the txn table and have
        config_label field then update the label of the msgs in execution session.
        Do everything in DB. 

    Args:
        request: A LabelConfigRequest object containing the execution session ID.

    Raises:
        peewee.PeeweeException: If any database errors occur.
    """

    try:
    # Retrieve new transactions for the execution session
        transactions_to_update = (
            Transactions
            .select(Transactions.to_vpa, Transactions.msgId)
            .where(Transactions.execution_id == request.execution_id)
        )

        # Extract unique VPAs from new transactions
        vpas_to_check = {transaction.to_vpa for transaction in transactions_to_update}

        # Retrieve historical labels for relevant VPAs
        historical_labels = (
            Transactions
            .select(Transactions.to_vpa, Transactions.config_label)
            .where(Transactions.to_vpa.in_(vpas_to_check))
            .group_by(Transactions.to_vpa)
            .having(peewee.SQL("COUNT(config_label) > 0"))  # Only include VPAs with existing config_label
        )

        # Update labels based on historical defaults
        for transaction in transactions_to_update:
            vpa = transaction.to_vpa
            # Directly iterate through the query results (no map needed)
            for historical_label in historical_labels:
                if historical_label.to_vpa == vpa:
                    Transactions.update(label=historical_label.config_label).where(
                        Transactions.msgId == transaction.msgId
                    ).execute()
                    break  # Stop iterating after finding the label for the current VPA

    except peewee.PeeweeException as e:
        raise peewee.PeeweeException("Error updating labels: {}".format(e))

    except Exception as e:
     raise e
  

def update_transactions_label(request: LabelVPARequest):
    """Updates the label field of transactions based on the input from user in 
        form of a POST request

    Args:
        request: A LabelVPARequest object containing the update details.

    Raises:
        peewee.DoesNotExist: If the transaction with the specified msgId is not found.
    """

    try:
    # Update the specific transaction with the msgId
        transaction = Transactions.get(Transactions.msgId == request.msgId)
        transaction.label = request.input_label

        # Update the config_label if apply_to_all is True
        if request.apply_to_all:
            transaction.config_label = request.input_label

        transaction.save()

        # Update all transactions with the same VPA (if applicable)
        if request.apply_to_all:
            Transactions.update(label=request.input_label).where(
                Transactions.to_vpa == request.vpa
            ).execute()

    except Transactions.DoesNotExist:
        raise peewee.DoesNotExist("Transaction with msgId {} not found".format(request.msgId))

    return transaction 

def update_label(user_input:LabelVPARequest):
    # from the interface post request in the form of LabelVPARequest
    # take msgId and update the `label` column 
    # if apply to all -> update all msgId where vpa = inuput.vpa 

    pass

if __name__ == '__main__':
   sample_request = LabelVPARequest(msgId='18df31c86960eddc',
                                    vpa='lazypaypvtltd.rzp@icici',
                                    input_label='LAZYPAY',
                                    apply_to_all=True,
                                    )
   print(update_transactions_label(sample_request))
