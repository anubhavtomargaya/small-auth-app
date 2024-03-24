from src.blueprints.actions.label import LabelVPARequest, update_transactions_label
from src.blueprints.gmail.process_encoded import extractBodyFromEncodedData
from src.blueprints.gmail.process_raw import extractCodedContentFromRawMessages, parse_gmail_message
from src.blueprints.gmail.view_transactions import get_transactions_view
from . import actions_app
import requests,json,datetime
from flask import current_app,jsonify,request, url_for, redirect,render_template
from ...common.session_manager import get_auth_token, is_logged_in,set_next_url
from ..google_auth.auth import get_user_info
from src.blueprints.gmail.fetch_by_token import fetch_for_token,TokenFetchRequest



@actions_app.route('/label/', methods=['POST'])
def update_label_by_user():
    """Updates transaction labels based on user input.

    Returns:
        A JSON response with the status of the update.
    """

    if request.method == 'POST':
        try:
            # Extract data from the request
            data = request.get_json()
            msgId = data.get('msgId')
            vpa = data.get('vpa')
            input_label = data.get('input_label')
            apply_to_all = data.get('apply_to_all', False)  # Default to False

            # Create the LabelVPARequest object
            label_request = LabelVPARequest(msgId=msgId, vpa=vpa, input_label=input_label, apply_to_all=apply_to_all)

            # Update transaction labels
            updated_transaction = update_transactions_label(label_request)

            # Return success response
            return jsonify({'message': f'Transaction label updated successfully {updated_transaction}'}), 200

        except Exception as e:
            # Handle exceptions (e.g., validation errors, database errors)
            return jsonify({'error': str(e)}), 400  # Bad request
    else:
        return jsonify(''), 405  # Method Not Allowed