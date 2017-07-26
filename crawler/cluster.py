import json
import os
import sys

from gensim import corpora, models, similarities

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from article_parser import Article
from shared.table import AzureTable
from shared.logger import Logger

class TopicCluster(object):
    def __init__(self, table):
        self._table = table
        self._urls = []
        self._articles = []

    def cluster(self, threshold):
        Logger.LogInformation('Retrieving documents')
        self.documents = [d for d in self._get_document()]
        Logger.LogInformation('Found %d documents' % len(self.documents))
        Logger.LogInformation('Finding dictionary elements')
        self._dictionary = corpora.Dictionary(self.documents)
        self._dictionary.compactify()
        Logger.LogInformation('Computing bag of word vectors')
        self._corpus = [self._dictionary.doc2bow(d) for d in self.documents]
        Logger.LogInformation('Computing Tfidf vectors')
        self._tfidf = models.TfidfModel(self._corpus)
        self._tfidf_corpus = [self._tfidf[d] for d in self._corpus]
        Logger.LogInformation('Generating the similarity index')
        self._index = similarities.MatrixSimilarity(self._tfidf_corpus)
        Logger.LogInformation('Forming clusters')
        num_clusters = self.form_clusters(threshold)
        Logger.LogInformation('Found %d clusters' % num_clusters)
        Logger.LogInformation('Finding relative sentiment in the same topic')
        self.find_relative_sentiment()
        return num_clusters

    def form_clusters(self, threshold):
        self._cluster_map = {}
        self._doc_cluster_map = {}
        i, cluster_idx = 0, 0
        for tfidf_vec in self._tfidf_corpus:
            i += 1
            if self._doc_cluster_map.has_key(i): continue
            cluster_idx += 1
            self._cluster_map[cluster_idx] = []
            self._doc_cluster_map[i] = cluster_idx
            for s in enumerate(self._index[tfidf_vec]):
                if s[1] < threshold: break
                self._doc_cluster_map[s[0]] = cluster_idx
                self._cluster_map[cluster_idx].append(s[0])
        return cluster_idx

    def find_relative_sentiment(self):
        min_docs_to_appear = 1
        for c in self._cluster_map:
            docs = self._cluster_map[c]
            # a map between entity and tuple(min_sentiment, max_sentiment, freq_count)
            entity_sentiments = {}
            for d in docs:
                article = self._articles[d]
                for entity in article.sentiment['entities']:
                    entity_name = entity['name']
                    if not entity_sentiments.has_key(entity_name):
                        entity_sentiments[entity_name] = [1.0, -1.0, 0]
                    entity_sentiments[entity_name][0] = min(entity_sentiments[entity_name][0], entity['sentiment'])
                    entity_sentiments[entity_name][1] = max(entity_sentiments[entity_name][1], entity['sentiment'])
                    entity_sentiments[entity_name][2] += 1
            for d in docs:
                article = self._articles[d]
                relative_sentiment = {}
                for entity in article.sentiment['entities']:
                    entity_name = entity['name']
                    if entity_sentiments[entity_name][2] > min_docs_to_appear:
                        min_sentiment = entity_sentiments[entity_name][0]
                        max_sentiment = entity_sentiments[entity_name][1]
                        mid_sentiment = (max_sentiment + min_sentiment) / 2
                        diff_sentiment = max_sentiment - min_sentiment
                        if diff_sentiment < 0.001: diff_sentiment = 1
                        relative_sentiment[entity_name] = (entity['sentiment'] - mid_sentiment) / diff_sentiment
                article.relative_sentiment = relative_sentiment

    def _get_document(self):
        for a in self._table.get_all():
            wordvec = []
            article = Article()
            article.__dict__ = json.loads(a)
            if article.sentiment == None: continue
            for entity in article.sentiment['entities']:
                wordvec.append(entity['name'])
            self._articles.append(article)
            self._urls.append(article.url)
            yield wordvec

if __name__=='__main__':
    storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
    storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
    table = AzureTable('Articles', storage_account_name, storage_account_key)
    cluster = TopicCluster(table)
    num_clusters = cluster.cluster(threshold=0.5)
