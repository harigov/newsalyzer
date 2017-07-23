import json
import socket
import sys
import os
import urllib2
from collections import deque

from article_parser import Article,ArticleParser

class WebCrawler(object):
    def __init__(self, article_parser, storage_path):
        self.article_parser = article_parser
        self._url_queue = deque()
        self._visited_url = {}
        self._storage_path = storage_path

    def crawl(self, start_url, url_limit, min_word_count=150):
        url_count = 0
        self._url_queue.append(start_url)    
        while url_count < url_limit and len(self._url_queue) > 0:
            url = self._url_queue.popleft()
            if url != None and url not in self._visited_url:                
                self._visited_url[url] = True
                article = self._crawl_website(url)
                if article == None: continue
                self._url_queue.extend(article.links)  
                if(article.word_count > min_word_count):
                    url_count += 1

    def _crawl_website(self, url):
        try:
            # Get all the data of an HTML page
            request = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"})
            response = urllib2.build_opener(urllib2.HTTPCookieProcessor).open(request)
            url_content = response.read()
            return self.article_parser.parse(url, url_content)
        except Exception, e:
            print 'Failed to crawl %s with exception: %s' % (url, e)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print "Too few arguments!"
        print "python crawler.py <start-url-string> <number-of-documents-to-crawl> <results-directory-path>"
    else:
        # Start/seed domain URL, homepage of nytimes
        start = sys.argv[1]
        # Upper limit on the number of URLs which need to be crawled
        urlLimit = sys.argv[2]
        # Path of the directory, where to write the documents
        resultsPath = sys.argv[3]

        # Check for valid path of the directory
        if not os.path.isdir(resultsPath):
            os.makedirs(resultsPath)

        article_parser = ArticleParser()
        crawler = WebCrawler(article_parser, resultsPath)
        crawler.crawl(start, int(urlLimit))
        print "Crawling Finished"
