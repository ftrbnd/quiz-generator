import random
import re

from phases.preprocessing import preprocess_text
from phases.question_creation import extract_entities_ner, extract_keywords_tfidf, extract_topics_lda, train_word_embeddings

def find_similar_words(word_model, word, top_n=5):
    """Find similar words using word embeddings"""
    if word_model is None:
        return []
    
    try:
        similar = word_model.wv.most_similar(word.lower(), topn=top_n)
        return [w for w, score in similar]
    except:
        return []

def generate_fill_blank_questions(text, n_questions=5):
    """Generate fill-in-the-blank questions using keywords"""
    sentences = preprocess_text(text)
    keywords = extract_keywords_tfidf(text, top_n=20)
    
    questions = []
    used_sentences = set()
    
    for keyword in keywords:
        if len(questions) >= n_questions:
            break
        
        for i, sentence in enumerate(sentences):
            if i in used_sentences:
                continue
            
            # Check if keyword appears in sentence (case insensitive)
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sentence, re.IGNORECASE):
                # Create blank
                blanked = re.sub(pattern, '_____', sentence, count=1, flags=re.IGNORECASE)
                questions.append({
                    'question': blanked,
                    'answer': keyword,
                    'type': 'fill_blank'
                })
                used_sentences.add(i)
                break
    
    return questions

def generate_mcq_questions(text, n_questions=5):
    """Generate multiple choice questions using NER and embeddings"""
    entities = extract_entities_ner(text)
    word_model = train_word_embeddings(text)
    sentences = preprocess_text(text)
    
    questions = []
    used_entities = set()
    
    for entity in entities:
        if len(questions) >= n_questions:
            break
        
        if entity['text'] in used_entities:
            continue
        
        # Find sentence containing this entity
        for sentence in sentences:
            if entity['text'] in sentence:
                # Generate distractors
                distractors = find_similar_words(word_model, entity['text'], top_n=3)
                
                # If not enough similar words, use other entities
                if len(distractors) < 3:
                    other_entities = [e['text'] for e in entities 
                                    if e['text'] != entity['text'] and e['label'] == entity['label']]
                    distractors.extend(other_entities[:3-len(distractors)])
                
                # Ensure we have exactly 3 distractors
                if len(distractors) < 3:
                    distractors.extend(['Option ' + str(i) for i in range(3-len(distractors))])
                
                options = [entity['text']] + distractors[:3]
                random.shuffle(options)
                
                questions.append({
                    'question': f"In the context: '{sentence}'\nWhat is the {entity['label'].lower()} mentioned?",
                    'options': options,
                    'answer': entity['text'],
                    'type': 'mcq'
                })
                used_entities.add(entity['text'])
                break
    
    return questions

def generate_topic_questions(text, n_questions=3):
    """Generate questions based on LDA topics"""
    topics = extract_topics_lda(text, n_topics=5)
    
    questions = []
    for i, topic_words in enumerate(topics[:n_questions]):
        topic_str = ', '.join(topic_words[:3])
        questions.append({
            'question': f"What main topic is discussed related to these concepts: {topic_str}?",
            'answer': f"Topic involving: {', '.join(topic_words)}",
            'type': 'topic'
        })
    
    return questions
