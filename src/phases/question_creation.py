import numpy as np
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from gensim.models import Word2Vec
from nltk.tokenize import word_tokenize
import spacy

from phases.preprocessing import get_stop_words, preprocess_text


try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("Please install spacy model: python -m spacy download en_core_web_sm")
    nlp = None    
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


def extract_keywords_tfidf(text, top_n=10):
    """Extract keywords using TF-IDF"""
    sentences = preprocess_text(text)
    
    if len(sentences) < 2:
        return []
    
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(sentences)
    feature_names = vectorizer.get_feature_names_out()
    
    # Get average TF-IDF scores
    avg_scores = np.mean(tfidf_matrix.toarray(), axis=0)
    top_indices = avg_scores.argsort()[-top_n:][::-1]
    
    keywords = [feature_names[i] for i in top_indices]
    return keywords

def extract_topics_lda(text, n_topics=3):
    """Extract topics using LDA"""
    sentences = preprocess_text(text)
    
    if len(sentences) < 2:
        return []
    
    vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
    doc_term_matrix = vectorizer.fit_transform(sentences)
    
    lda = LatentDirichletAllocation(n_components=min(n_topics, len(sentences)), 
                                    random_state=42, max_iter=10)
    lda.fit(doc_term_matrix)
    
    feature_names = vectorizer.get_feature_names_out()
    topics = []
    
    for topic_idx, topic in enumerate(lda.components_):
        top_indices = topic.argsort()[-5:][::-1]
        topic_words = [feature_names[i] for i in top_indices]
        topics.append(topic_words)
    
    return topics

def extract_entities_ner(text):
    """Extract named entities using spaCy"""
    if nlp is None:
        return []
    
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'ORG', 'GPE', 'DATE', 'EVENT', 'PRODUCT']:
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })
    
    return entities

def train_word_embeddings(text):
    """Train Word2Vec embeddings"""
    sentences = preprocess_text(text)
    tokenized = [word_tokenize(s.lower()) for s in sentences]

    # Filter out stopwords and short words
    stop_words = get_stop_words()
    tokenized = [[w for w in sent if w.isalnum() and w not in stop_words and len(w) > 2] 
                for sent in tokenized]
    
    if len(tokenized) < 2:
        return None
    
    model = Word2Vec(sentences=tokenized, vector_size=50, window=5, 
                    min_count=1, workers=2, seed=42)
    return model