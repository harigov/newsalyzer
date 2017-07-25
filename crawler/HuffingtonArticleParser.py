import urlparse
import os
from bs4 import BeautifulSoup
import re
from article_parser import ArticleParser

class HuffingtonArticleParser(ArticleParser):
    def parse(self, url, article_text):
        ArticleParser.parse(self,url,article_text)

    def _get_title(self):
        head = self._soup.find('headline__title')
        if head != None:
            title = head.find('headline__title')
            if title != None:
                return title.getText()
        return ''

    def _get_date(self):
        date = self._soup.find('span', {'class' : 'timestamp__date--published'})
        if(date != None):
            return date.getText().encode('utf-8')
        else:
            date = self._soup.find('meta', {'name' : 'DISPLAYDATE'})
            if date != None:
                date = date.get('content')
                if date != None:
                    return date.encode('utf-8')
        return ''

    def _get_article_text(self):
        content = ''
        for story_element in self._soup.findAll('div', {'class' : 'bn-content-list-text'}):
            if story_element != None:
                # Remove newlines
                content += re.sub(r"\n+", " ", story_element.getText())
        return content
