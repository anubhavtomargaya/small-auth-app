from flask import Flask,redirect, url_for,render_template,current_app,jsonify
from flask_cors import CORS,cross_origin
import logging
from .utils.logger import fh
from .blueprints.google_auth import google_auth
from .common.session_manager import *

logging.basicConfig(level=logging.INFO)  



def create_app():
    app = Flask(__name__)
    # app.logger.addHandler(file_handler)
    app.logger.addHandler(fh)
    app.logger.info('Flask app started')
    CORS(app)
    app.logger.info('Flask app CORSed')

    app.secret_key = "MYSK3Y"
    # # os.environ.get("FN_FLASK_SECRET_KEY", default=False)

    app.register_blueprint(google_auth, url_prefix='/google')
    app.logger.info('Flask bp registerd, %s',"/google")

    return app 

app = create_app()


@app.route('/login',methods=['GET'])
def login():
    if is_logged_in():

        current_app.logger.info('logged in , %s',get_next_url())
        return redirect(url_for('home'))
    else:
        current_app.logger.info('not logged in , %s',get_next_url())
        set_next_url(url_for('home'))
        current_app.logger.info('next url set, %s',url_for('home'))
        current_app.logger.info('next url get, %s',get_next_url())
        
        return redirect(url_for('google_auth.login'))

@app.route('/',methods=['GET'])
def home():
    if not is_logged_in():
        set_next_url(url_for('home'))
        current_app.logger.info('next url set, %s',url_for('home'))
        current_app.logger.info('next url get, %s',get_next_url())
        
        return render_template('login.html')
        # return redirect(url_for('login'))
    
    # Render the home page with a table or dashboard
    return render_template('home.html')

@app.route('/test',methods=['GET'])
def test():
    # if not is_logged_in():
    return render_template('index.html')
        # return redirect(url_for('login'))
    # Render the home page with a table or dashboard
    # return render_template('home.html')

@app.route('/logout',methods=['GET'])
def logout():
    if not is_logged_in():
        return redirect(url_for('login'))
    # Render the home page with a table or dashboard
    clear_auth_session()  # Clear session data
    return render_template('login.html')

@app.route('/session',methods=['GET'])
def debug():
    # if not is_logged_in():pass
        # return redirect(url_for('login'))
    # Render the home page with a table or dashboard
    # else:
        return jsonify(get_session_items())
    # return redirect(url_for('login'))  
