import urlparse
import os
from bs4 import BeautifulSoup
import re
from article_parser import ArticleParser

class CNNArticleParser(ArticleParser):
    def parse(self, url, article_text):
        ArticleParser.parse(self,url,article_text)

    def _get_title(self):
        head = self._soup.find('pg-headline')
        if head != None:
            title = head.find('pg-headline')
            if title != None:
                return title.getText()
        return ''

    def _get_date(self):
        date = self._soup.find('p', {'class' : 'update-time'})
        if(date != None):
            return date.getText().encode('utf-8')
        else:
            date = self._soup.find('meta', {'name' : 'DISPLAYDATE'})
            if date != None:
                date = date.get('content')
                if date != None:
                    return date.encode('utf-8')
        return ''

    def _get_link_elements(self):
        return self._soup.findAll('div', {'class' : 'story'}) + self._soup.findAll('article', {'class' : 'story'})

    def _get_article_text(self):
        content = ''
        for story_element in self._soup.findAll('p', {'class' : 'zn-body__paragraph'}):
            if story_element != None:
                # Remove newlines
                content += re.sub(r"\n+", " ", story_element.getText())
        return content
