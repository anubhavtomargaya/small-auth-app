from flask import Flask, render_template, jsonify
from authlib.integrations.flask_client import OAuth
 
app = Flask(__name__)
 
# app.secret_key = 'key'
'''
    Set SERVER_NAME to localhost as twitter callback
    url does not accept 127.0.0.1
    Tip : set callback origin(site) for facebook and twitter
    as http://domain.com (or use your domain name) as this provider
    don't accept 127.0.0.1 / localhost
'''
 
# app.config['SERVER_NAME'] = 'localhost:5000/'
# oauth = OAuth(app)
 
@app.route('/')
def index():
    return True
    # return render_template('/templates/index.html')
 

if __name__ == "__main__":
    app.run(debug=True)