#!/bin/python
import argparse
import os
import sys

from sentiment_extractor import SentimentExtractor
from article_parser import Article, ArticleParser, CNNArticleParser
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
    sentiment = SentimentExtractor()

    for source in news_sources:
        Logger.LogInformation('Crawling '+ source['Name'])
        crawler = WebCrawler(source['Parser'], source['Name'], table, sentiment)
        count = 0
        for seed_url in source['SeedURLs']:
            Logger.LogInformation('\tCrawling ' + seed_url)
            count += crawler.crawl(seed_url, int(args.max_seed_limit))
            if count > args.max_limit: break
        Logger.LogInformation('Total %d new articles found' % count)
    Logger.LogInformation("Crawling Finished")
