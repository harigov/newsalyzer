import os
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, jsonify, make_response
import json

from google.cloud import language

from decorators import Monitor
from blob_storage import BlobStorage

app = Flask(__name__)
#app.wsgi_app = WSGIApplication(app.config['APPINSIGHTS_INSTRUMENTATION_KEY'], app.wsgi_app)

if os.environ.has_key('STORAGE_ACCOUNT_NAME'):
    local_key_file = 'private/google-nlp-key.json'
    blob_storage = BlobStorage(os.environ['STORAGE_ACCOUNT_NAME'], os.environ['STORAGE_ACCOUNT_KEY'])
    blob_storage.download_file('private', 'google-nlp-key.json', local_key_file)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = local_key_file

@app.route('/')
@Monitor.api()
def index():
    return 'Newsalyzer'

@app.route('/get-sentiment', endpoint='get_sentiment')
@Monitor.api()
def get_sentiment():
    language_client = language.Client(api_version='v1beta2')
    document = language_client.document_from_text(request.args['text'])
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
