import argparse
import os
import sys

from multiprocessing.pool import ThreadPool
from sentiment_extractor import SentimentExtractor
from article_parser import Article, ArticleParser
from CNNArticleParser import CNNArticleParser
from HuffingtonArticleParser import HuffingtonArticleParser
from BreitbartArticleParser import BreitbartArticleParser
from FoxArticleParser import FoxArticleParser
from WashingtonPostParser import WashingtonPostParser
from YahooMailParser import YahooMailParser
from crawler import WebCrawler

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from shared.logger import Logger
from shared.blob_storage import BlobStorage
from shared.table import AzureTable

# Holds information about different news sources that
# are supported and their seed urls
news_sources = [
    {
        'Name': 'www.nytimes.com', # It has to be the website name
        'Parser': ArticleParser(),
        'SeedURLs': [
            'https://www.nytimes.com/section/world',
            'https://www.nytimes.com/section/us',
            'https://www.nytimes.com/section/politics',
            'https://www.nytimes.com/pages/opinion',
            'https://www.nytimes.com/pages/business',
            'https://www.nytimes.com/section/technology',
            'https://www.nytimes.com/section/science',
            'https://www.nytimes.com/section/health'
        ]
    },
    {
        'Name': 'www.cnn.com',
        'Parser': CNNArticleParser(),
        'SeedURLs': [
            'http://money.cnn.com/',
            'http://www.cnn.com/us',
            'http://www.cnn.com/world',
            'http://www.cnn.com/politics',
            'http://www.cnn.com/opinions',
            'http://www.cnn.com/entertainment',
            'http://www.cnn.com/health',
            'http://money.cnn.com/technology/',
            'http://www.cnn.com/style',
            'http://www.cnn.com/travel'
        ]
    },
    {
        'Name': 'www.huffingtonpost.com',
        'Parser': HuffingtonArticleParser(),
        'SeedUrls': [
            'http://www.huffingtonpost.com/section/politics',
            'http://www.huffingtonpost.com/section/technology',
            'http://www.huffingtonpost.com/section/education',
            'http://www.huffingtonpost.com/section/business',
            'http://highline.huffingtonpost.com/',
            'http://www.huffingtonpost.com/section/science',
            'http://www.huffingtonpost.com/section/weird-news',
            'http://testkitchen.huffingtonpost.com/',
            'http://www.huffingtonpost.com/section/college'
        ]
    },
    {
        'Name': 'www.breitbart.com/',
        'Parser': BreitbartArticleParser(),
        'SeedUrls': [
            'http://www.breitbart.com/big-government/',
            'http://www.breitbart.com/big-journalism/',
            'http://www.breitbart.com/big-hollywood/',
            'http://www.breitbart.com/national-security/',
            'http://www.breitbart.com/tech/',
            'http://www.breitbart.com/sports/',
            'http://www.breitbart.com/news/'

        ]
    },
    {
        'Name': 'www.foxnews.com/' , 
        'Parser': FoxArticleParser(),
        'SeedUrls': [
            'http://www.foxnews.com/politics.html',
            'http://www.foxnews.com/us.html',
            'http://www.foxnews.com/opinion.html',
            'http://www.foxnews.com/entertainment.html',
            'http://www.foxbusiness.com/',
            'http://www.foxnews.com/tech.html',
            'http://www.foxnews.com/science.html',
            'http://www.foxnews.com/health.html',
            'http://www.foxnews.com/travel.html',
            'http://www.foxnews.com/lifestyle.html',
            'http://www.foxnews.com/world.html'
        ]
    },
    {
        'Name': 'www.washingtonpost.com/',
        'Parser': WashingtonPostParser(),
        'SeedURLs': [
            'http://www.washingtonpost.com/politics/',
            'https://www.washingtonpost.com/local/',
            'https://www.washingtonpost.com/sports/',
            'https://www.washingtonpost.com/national/',
            'https://www.washingtonpost.com/world/',
            'https://www.washingtonpost.com/business/',
            'https://www.washingtonpost.com/entertainment/',
            'https://www.washingtonpost.com/realestate/'
        ]
    },
     {
        'Name': 'https://www.yahoo.com/news/',
        'Parser': YahooMailParser(),
        'SeedURLs': [
            'https://www.yahoo.com/news/us/',
            'https://www.yahoo.com/news/world/',
            'https://www.yahoo.com/news/politics/',
            'https://www.yahoo.com/news/science/',
            'https://www.yahoo.com/news/odd/',
            'https://www.yahoo.com/news/originals/'
         ]
    }
]

def download_nlp_key(storage_account_name, storage_account_key):
    local_key_file = '.private/google-nlp-key.json'
    if not os.path.exists(local_key_file): 
        base_dir_name = os.path.dirname(local_key_file)
        if base_dir_name != '' and not os.path.exists(base_dir_name):
            os.mkdir(base_dir_name)
        Logger.LogInformation('Downloading the private key file')
        blob_storage = BlobStorage(storage_account_name, storage_account_key)
        blob_storage.download_file('private', 'google-nlp-key.json', local_key_file)
        Logger.LogInformation('Successfully downloaded the key')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = local_key_file

def crawl_thread_func(*args):
    source, seed_url, crawler, max_seed_limit = args[0]
    count = 0
    try:
        Logger.LogInformation('Crawling '+ source['Name'])
        count = crawler.crawl(seed_url, int(args.max_seed_limit))
    except Exception,e:
        Logger.LogError('Failed to crawl through seed url %s for source %s' % (seed_url, source['Name']))
    Logger.LogInformation('Total %d new articles found' % count)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='worker', description="Worker that crawls news sources and extracts articles")
    parser.add_argument('--wait', dest='wait_time', type=int, default=120,
                            help='Specify the wait time in minutes. ' +
                            'If command takes more than this time, it will be cancelled.')
    parser.add_argument('--limit', dest='max_limit', type=int, default=100,
                            help='Specify the maximum number of articles to download per source.' +
                            'If more articles are found, they will be ignored.')
    parser.add_argument('--seed_limit', dest='max_seed_limit', type=int, default=10,
                            help='Specify the maximum number of articles to download from a single seed.' +
                            'If more articles are found, they will be ignored.')
    args = parser.parse_args()

    storage_account_name = os.environ['STORAGE_ACCOUNT_NAME']
    storage_account_key = os.environ['STORAGE_ACCOUNT_KEY']
    download_nlp_key(storage_account_name, storage_account_key)
    table = AzureTable('Articles', storage_account_name, storage_account_key)
    visited_urls = {}
    for url in table.get_all_row_keys(source):
        visited_urls[url] = True
    sentiment = SentimentExtractor()

    pool = ThreadPool()
    thread_inputs = []
    for source in news_sources:
        crawler = WebCrawler(source['Parser'], source['Name'], table, sentiment, visited_urls)
        Logger.LogInformation('Crawling '+ source['Name'])
        for seed_url in source['SeedURLs']:
            thread_inputs.append((source['Name'], seed_url, crawler, args.max_seed_limit))
    pool.map(crawl_thread_func, thread_inputs)
    Logger.LogInformation("Waiting for threads to finish")
    pool.close()
    pool.join()
    Logger.LogInformation("Crawling Finished")
