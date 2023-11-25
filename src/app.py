from flask import Flask
from flask_cors import CORS,cross_origin
import logging
from logger import fh

logging.basicConfig(level=logging.INFO)  



def create_app():
    app = Flask(__name__)
    # app.logger.addHandler(file_handler)
    app.logger.addHandler(fh)
    app.logger.info('Flask app started')
    CORS(app)
    app.logger.info('Flask app CORSed')
    return app 

app = create_app()