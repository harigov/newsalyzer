import urlparse
import os
from bs4 import BeautifulSoup
import re
from article_parser import ArticleParser

class BreitbartArticleParser(ArticleParser):
    def _get_title(self):
        head = self._soup.find('header', {'class': 'articleheader'})
        if head != None:
            title = head.find('h1')
            if title != None:
                return title.getText()
        return ''

    def _get_date(self):
        date = self._soup.find('span', {'class' : 'bydate'})
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
                # exclude links that aren't from the same domain
                index = url.find(self.base_domain)
                if(index == -1): continue
                links.append(url)
        return links

    def _get_link_elements(self):
        return self._soup.findAll('h2', {'class' : 'title'})

    def _get_article_text(self):
        content = ''
        for story_element in self._soup.findAll('div', {'class' : 'entry-content'}):
            if story_element != None:
                # Remove newlines
                for h2_element in story_element.findAll('h2'):
                    content += re.sub(r"\n+", " ", h2_element.getText())
                for p_element in story_element.findAll('p'):
                    content += re.sub(r"\n+", " ", p_element.getText())
        return content
