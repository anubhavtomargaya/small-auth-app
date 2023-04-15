from flask import Flask
from flask_cors import CORS,cross_origin
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
fh = logging.FileHandler('test.log')
fh.setLevel(logging.INFO)
# logger.addHandler(fh)

app = Flask(__name__)
CORS(app)

