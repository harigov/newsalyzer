#!/bin/python
import argparse
import os
import sys

from article_parser import Article, ArticleParser
from crawler import WebCrawler
from table import AzureTable

# Holds information about different news sources that
# are supported and their seed urls
news_sources = [
    {
        'Name': 'nytimes.com',
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
    }
]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='worker', description="Worker that crawls news sources and extracts articles")
    parser.add_argument('--dir', dest='local_dir', default=os.getcwd(), 
                            help='Directory that contains all the downloaded articles.')
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

    # Check for valid path of the directory
    if not os.path.isdir(args.local_dir):
        os.makedirs(args.local_dir)

    table = AzureTable('Articles', os.environ['STORAGE_ACCOUNT_NAME'], os.environ['STORAGE_ACCOUNT_KEY'])

    for source in news_sources:
        print 'Crawling', source['Name']
        crawler = WebCrawler(source['Parser'], source['Name'], table)
        count = 0
        for seed_url in source['SeedURLs']:
            print '\tCrawling', seed_url
            count += crawler.crawl(seed_url, int(args.max_seed_limit))
            if count > args.max_limit: break
        print 'Total %d new articles found' % count
    print "Crawling Finished"
