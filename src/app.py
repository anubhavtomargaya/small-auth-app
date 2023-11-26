""" 
Using application factory, i.e. create_app() contains all the steps involved in
creating the flask application. due to which some routes are also inside this 
function. They can be added as a blueprint but I am using these as tools while 
developement. Run this with run.py" 
"""
from flask import Flask,redirect, url_for,render_template,current_app,jsonify
from flask_cors import CORS,cross_origin
import logging
from .utils.logger import fh
from .blueprints.google_auth import google_auth
from .blueprints.gmail import gmail_app
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

    app.register_blueprint(gmail_app, url_prefix='/api/v1')
    app.logger.info('Flask bp registerd, %s',"/api/v1")

   

# app = create_app()

    #home is always rendering a template
    @app.route('/',methods=['GET'])
    def home():
        if not is_logged_in():
            set_next_url(url_for('home'))
            current_app.logger.info('next url set, %s',url_for('home'))
            current_app.logger.info('next url get, %s',get_next_url())
            
            return render_template('login.html')
        else:
            return render_template('home.html')

    #login & logout routes only redirect
    @app.route('/login',methods=['GET'])
    def login():
        if is_logged_in():

            current_app.logger.info('logged in ,next url %s',get_next_url())
            return redirect(url_for('home'))
        else:
            current_app.logger.info('not logged in , %s',get_next_url())
            current_app.logger.info('next url get, %s',get_next_url())
            
            return redirect(url_for('google_auth.login'))

    @app.route('/logout',methods=['GET'])
    def logout():
        if not is_logged_in():
            return redirect(url_for('login'))
        # Render the home page with a table or dashboard
        clear_auth_session()  # Clear session data
        return redirect(url_for('home'))

    #test a route to debug beside home
    @app.route('/test',methods=['GET'])
    def test():
        # if not is_logged_in():
        return render_template('index_copy.html')
            # return redirect(url_for('login'))
        # Render the home page with a table or dashboard
        # return render_template('home.html')

        
    @app.route('/session',methods=['GET'])
    def debug():
        # if not is_logged_in():pass
            # return redirect(url_for('login'))
        # Render the home page with a table or dashboard
        # else:
            return jsonify(get_session_items())
        # return redirect(url_for('login'))  

    return app 