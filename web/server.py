import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, jsonify, make_response
import json

from google.cloud import language

from decorators import Monitor
from blob_storage import BlobStorage
from logger import Logger

app = Flask(__name__)
app.config['DEBUG']=True
#app.wsgi_app = WSGIApplication(app.config['APPINSIGHTS_INSTRUMENTATION_KEY'], app.wsgi_app)

if os.environ.has_key('STORAGE_ACCOUNT_NAME'):
    try:
        storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
        storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
        local_key_file = 'private/google-nlp-key.json'
        base_dir_name = os.path.dirname(local_key_file)
        if base_dir_name != '' and not os.path.exists(base_dir_name):
            os.mkdir(base_dir_name)
        Logger.LogInformation('Downloading the private key file')
        blob_storage = BlobStorage(storage_account_name, storage_account_key)
        blob_storage.download_file('private', 'google-nlp-key.json', local_key_file)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = local_key_file
        Logger.LogInformation('Successfully downloaded the private key file')
    except Exception,e:
        Logger.LogError('Failed to download private key: ' + e.msg)

@app.route('/', endpoint='index')
@Monitor.api()
def index():
    return 'Newsalyzer'

@app.route('/.well-known/<path:path>', endpoint='get_acme_challenge')
@Monitor.api()
def get_acme_challenge(path):
    return open(os.path.join('.well-known', path), 'r').read()

@app.route('/get-sentiment', endpoint='get_sentiment')
@Monitor.api()
def get_sentiment():
    language_client = language.Client(api_version='v1beta2')
    document = language_client.document_from_text(request.data)
    # Detects the sentiment of the text
    sentiment = document.analyze_sentiment().sentiment
    entity_response = document.analyze_entity_sentiment()
    response = {
        'score' : sentiment.score,
        'magnitude' : sentiment.magnitude,
        'entities' : [ { 'name': e.name, 'type': e.entity_type, 'sentiment' : e.sentiment.score, 'magnitude': e.sentiment.magnitude } for e in entity_response.entities]
    }

    return json.dumps(response), 200, {'ContentType':'application/json'}

if __name__=='__main__':
    app.run()
