import hashlib
import os
import sys
import urlparse
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, jsonify, make_response
import json

from decorators import Monitor

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from shared.logger import Logger
from shared.table import AzureTable

app = Flask(__name__)
app.config['DEBUG']=True
#app.wsgi_app = WSGIApplication(app.config['APPINSIGHTS_INSTRUMENTATION_KEY'], app.wsgi_app)

storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
table = AzureTable('Articles', storage_account_name, storage_account_key)

@app.route('/', endpoint='index')
@Monitor.api()
def index():
    return 'Newsalyzer'

@app.route('/.well-known/<path:path>', endpoint='get_acme_challenge')
@Monitor.api()
def get_acme_challenge(path):
    return open(os.path.join('.well-known', path), 'r').read()

@app.route('/get-sentiment', methods=['GET'], endpoint='get_sentiment')
@Monitor.api()
def get_sentiment():
    url = request.args['url']
    source_name = urlparse.urlparse(url).hostname
    url_hash = hashlib.sha256(url).hexdigest()
    json_data = table.get(source_name, url_hash)
    if json_data != None:
        data = json.loads(json_data)
        if data.has_key('sentiment'):
            return json.dumps(data['sentiment']), 200, {'ContentType':'application/json'}
    return json.dumps({ 'message': 'No sentiment data available for %s' % url }), 404, {'ContentType':'application/json'}

if __name__=='__main__':
    app.run()
