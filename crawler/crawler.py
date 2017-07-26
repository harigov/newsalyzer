import hashlib
import json
import socket
import sys
import os
import urllib2
from collections import deque

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from shared.logger import Logger

class WebCrawler(object):
    def __init__(self, article_parser, source, table, sentiment_extractor, visited_urls):
        self._article_parser = article_parser
        self._source = source
        self._table = table
        self._sentiment_extractor = sentiment_extractor
        self._url_queue = deque()
        self._visited_urls = visited_urls

    def crawl(self, start_url, url_limit, min_word_count=150):
        url_count = 0
        self._url_queue.append(start_url)    
        # start_url is usually a RSS feed with links to bunch of
        # articles. We should parse it even if we visited it earlier
        start_url_hash = self._get_url_hash(start_url)
        if start_url_hash in self._visited_urls:
            del self._visited_urls[start_url_hash]
        while url_count < url_limit and len(self._url_queue) > 0:
            url = self._url_queue.popleft()
            url_hash = self._get_url_hash(url)
            if url != None and not url_hash in self._visited_urls:
                self._visited_urls[url_hash] = True
                Logger.LogDebug('\t\tVisiting %s' % url)
                article = self._crawl_website(url)
                if article==None: continue
                if self._sentiment_extractor != None:
                    Logger.LogDebug('\t\tExtracting sentiment for %s' % url)
                    article.sentiment = self._sentiment_extractor.find_sentiment(article.content)
                if article.content!=None and article.title!=None:
                    article_json = json.dumps(article.__dict__)
                    self._table.set(self._source, url_hash, article_json)
                self._url_queue.extend(article.links)
                if(article.word_count > min_word_count):
                    url_count += 1
        return url_count

    def _get_url_hash(self, url):
        return hashlib.sha256(url).hexdigest()

    def _crawl_website(self, url):
        try:
            # Get all the data of an HTML page
            request = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
            response = urllib2.build_opener(urllib2.HTTPCookieProcessor).open(request)
            url_content = response.read()
            return self._article_parser.parse(url, url_content)
        except Exception, e:
            print 'Failed to crawl %s with exception: %s' % (url, e)
        return None
