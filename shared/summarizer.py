from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

# summarizer requires this to work
import nltk
nltk.download('punkt')

class ArticleSummarizer(object):
    def __init__(self):
        self._language = "english"
        self._max_sentence_count = 2

    def summarize(self, text):
        try:
            parser = PlaintextParser.from_string(text, Tokenizer(self._language))
            stemmer = Stemmer(self._language)
            summarizer = Summarizer(stemmer)
            summarizer.stop_words = get_stop_words(self._language)
            output = ''
            for sentence in summarizer(parser.document, self._max_sentence_count):
                output += str(sentence)
            return output
        except Exception, e:
            return ''

if __name__ == "__main__":
    text = ""
    summarizer = ArticleSummarizer()
    print summarizer.summarize(text)