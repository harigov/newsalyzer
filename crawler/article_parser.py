import urlparse
import os
from bs4 import BeautifulSoup
import re
import sys

sys.path.insert(0,os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

from shared.summarizer import ArticleSummarizer

class Article(object):
    def __init__(self):
        self.url = ''
        self.content = ''
        self.word_count = 0
        self.title = ''
        self.date = ''
        self.keywords = ''
        self.links = []
        self.sentiment = {}
        self.summary = ''
        self.relative_sentiment = {}

class ArticleParser(object):
    def __init__(self):
        self._summarizer = ArticleSummarizer()

    def parse(self, url, article_text):
        self.url = url
        self.base_domain = urlparse.urlparse(url).hostname
        self.text = article_text
        self._soup = BeautifulSoup(self.text, "html.parser")
        article = Article()
        article.url = self.url
        article.content = self._get_article_text()
        article.word_count = len(article.content.split())
        article.links = self._extract_links()
        article.title = self._get_title()
        article.keywords = self._get_keywords()
        article.date = self._get_date()
        article.summary = self._summarizer.summarize(article.content)
        return article

    def _extract_links(self):
        links = []
        for link_element in self._get_link_elements():
            for href_element in link_element.findAll('a', href = True):
                url = href_element.get('href').encode('utf-8')
                # exclude non-article links and refs
                index = url.find(".html")
                if index == -1: continue
                # exclude links that aren't from the same domain
                index = url.find(self.base_domain)
                if(index == -1): continue
                links.append(url)
        return links

    def _get_date(self):
        date = self._soup.find('li', {'class' : 'date'})
        if(date != None):
            return date.getText().encode('utf-8')
        else:
            date = self._soup.find('meta', {'name' : 'DISPLAYDATE'})
            if date != None:
                date = date.get('content')
                if date != None:
                    return date.encode('utf-8')
        return ''

    def _get_title(self):
        head = self._soup.find('head')
        if head != None:
            title = head.find('title')
            if title != None:
                return title.getText()
        return ''

    def _get_keywords(self):
        meta = self._soup.find('meta', {'name' : 'keywords'})
        if(meta != None):
            meta = meta.get('content')
            return meta.encode('utf-8')
        return ''

    def _get_link_elements(self):
        return self._soup.findAll('div', {'class' : 'story'}) + self._soup.findAll('article', {'class' : 'story'})

    def _get_article_text(self):
        content = ''
        for story_element in self._soup.findAll('p', {'class' : 'story-body-text'}):
            if story_element != None:
                # Remove newlines
                content += re.sub(r"\n+", " ", story_element.getText())
        return content
