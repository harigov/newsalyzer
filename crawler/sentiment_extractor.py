from google.cloud import language

class SentimentExtractor(object):
    def __init__(self):
        pass

    def find_sentiment(self, text):
        language_client = language.Client(api_version='v1beta2')
        document = language_client.document_from_text(text)
        # Detects the sentiment of the text
        sentiment = document.analyze_sentiment().sentiment
        entity_response = document.analyze_entity_sentiment()
        response = {
            'score' : sentiment.score,
            'magnitude' : sentiment.magnitude,
            'entities' : [ { 'name': e.name, 'type': e.entity_type, 'sentiment' : e.sentiment.score, 'magnitude': e.sentiment.magnitude } for e in entity_response.entities]
        }
        return response