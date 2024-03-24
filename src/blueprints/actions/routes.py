from src.blueprints.gmail.process_encoded import extractBodyFromEncodedData
from src.blueprints.gmail.process_raw import extractCodedContentFromRawMessages, parse_gmail_message
from src.blueprints.gmail.view_transactions import get_transactions_view
from . import actions_app
import requests,json,datetime
from flask import current_app,jsonify,request, url_for, redirect,render_template
from ...common.session_manager import get_auth_token, is_logged_in,set_next_url
from ..google_auth.auth import get_user_info
from src.blueprints.gmail.fetch_by_token import fetch_for_token,TokenFetchRequest



@actions_app.route('/label/',methods=['POST']) 
def get_transactions_final():
    mthd = request.method 
    args = request.args
    exec_id = args.get('id')
    start = args.get('start')
    end = args.get('end')

    if mthd =='POST':
        return jsonify(get_transactions_view(exec_session_id=exec_id,
                                             start=start,
                                             end=end,
                                             df=False))