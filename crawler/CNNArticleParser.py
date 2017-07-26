import urlparse
import os
from bs4 import BeautifulSoup
import re
from article_parser import ArticleParser

class CNNArticleParser(ArticleParser):
    def _get_title(self):
        title = self._soup.find('h1', {'class': 'pg-headline'})
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

    def _extract_links(self):
        links = []
        for link_element in self._get_link_elements():
            for href_element in link_element.findAll('a', href = True):
                url = href_element.get('href').encode('utf-8')
                # exclude non-article links and refs
                index = url.find(".html")
                if index == -1: continue
                if not url.startswith('https:') and not url.startswith('http:'):
                    url = 'https://' + self.base_domain + url
                # exclude links that aren't from the same domain
                links.append(url)
        return links

    def _get_link_elements(self):
        return self._soup.findAll('article', {'class' : 'cd'})

    def _get_article_text(self):
        content = ''
        for story_element in self._soup.findAll('p', {'class' : 'zn-body__paragraph'}):
            if story_element != None:
                # Remove newlines
                content += re.sub(r"\n+", " ", story_element.getText())
        for story_element in self._soup.findAll('div', {'class' : 'zn-body__paragraph'}):
            if story_element != None:
                # Remove newlines
                content += re.sub(r"\n+", " ", story_element.getText())
        return content
