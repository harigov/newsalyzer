from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, jsonify, make_response
import json

app = Flask(__name__)
#app.wsgi_app = WSGIApplication(app.config['APPINSIGHTS_INSTRUMENTATION_KEY'], app.wsgi_app)

@app.route('/')
def index():
    return 'Newsalyzer'

@app.route('/get-sentiment', endpoint='get_sentiment')
def get_sentiment():
    from google.cloud import language
    language_client = language.Client()
    text = request.args['text']
    document = language_client.document_from_text(text)
    # Detects the sentiment of the text
    sentiment = document.analyze_sentiment().sentiment
    entity_response = document.analyze_entities()
    response = {
        'score' : sentiment.score,
        'magnitude' : sentiment.magnitude,
        'entities' : [ { 'name': e.name, 'type': e.entity_type, 'sentiment' : e.sentiment } for e in entity_response.entities]
    }
    return json.dumps(response), 200, {'ContentType':'application/json'}

if __name__=='__main__':
    app.run()