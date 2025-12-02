import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def preprocess_text(text):
    """Clean and preprocess text"""
    sentences = sent_tokenize(text)
    return sentences

def get_stop_words():
    stop_words = set(stopwords.words('english'))
    return stop_words
