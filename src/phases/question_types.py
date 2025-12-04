import random
import re

from . import preprocessing, algorithms

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
    sentences = preprocessing.preprocess_text(text)
    keywords = algorithms.extract_keywords_tfidf(text, top_n=20)
    
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
    entities = algorithms.extract_entities_ner(text)
    word_model = algorithms.train_word_embeddings(text)
    sentences = preprocessing.preprocess_text(text)
    
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
    topics = algorithms.extract_topics_lda(text, n_topics=5)
    
    questions = []
    for i, topic_words in enumerate(topics[:n_questions]):
        topic_str = ', '.join(topic_words[:3])
        questions.append({
            'question': f"What main topic is discussed related to these concepts: {topic_str}?",
            'answer': f"Topic involving: {', '.join(topic_words)}",
            'type': 'topic'
        })
    
    return questions

def generate_true_false_questions(text, n_questions=5):
    sentences = preprocessing.preprocess_text(text)
    entities = algorithms.extract_entities_ner(text)
    keywords = algorithms.extract_keywords_tfidf(text, top_n=20)
    
    questions = []
    used_sentences = set()
    
    # Strategy 1: Use sentences with entities as TRUE statements
    for entity in entities:
        if len(questions) >= n_questions:
            break
        
        for i, sentence in enumerate(sentences):
            if i in used_sentences:
                continue
            
            if entity['text'] in sentence:
                # Create a TRUE question from the original sentence
                questions.append({
                    'question': sentence,
                    'answer': 'True',
                    'explanation': f"This statement is directly from the text.",
                    'type': 't/f'
                })
                used_sentences.add(i)
                
                # Optionally create a FALSE question by replacing the entity
                if len(questions) < n_questions:
                    # Find a different entity of the same type for replacement
                    other_entities = [e['text'] for e in entities 
                                    if e['text'] != entity['text'] and e['label'] == entity['label']]
                    
                    if other_entities:
                        false_sentence = sentence.replace(entity['text'], other_entities[0], 1)
                        questions.append({
                            'question': false_sentence,
                            'answer': 'False',
                            'explanation': f"The text actually mentions '{entity['text']}', not '{other_entities[0]}'.",
                            'type': 't/f'
                        })
                break
    
    # Strategy 2: Create statements with keyword substitution for remaining questions
    for keyword in keywords:
        if len(questions) >= n_questions:
            break
        
        for i, sentence in enumerate(sentences):
            if i in used_sentences:
                continue
            
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sentence, re.IGNORECASE):
                # TRUE question
                questions.append({
                    'question': sentence,
                    'answer': 'True',
                    'explanation': 'This statement is from the original text.',
                    'type': 't/f'
                })
                used_sentences.add(i)
                break
    
    return questions[:n_questions]


def generate_short_answer_questions(text, n_questions=5):
    sentences = preprocessing.preprocess_text(text)
    keywords = algorithms.extract_keywords_tfidf(text, top_n=20)
    entities = algorithms.extract_entities_ner(text)
    
    questions = []
    used_sentences = set()
    
    # Question templates based on question words
    question_templates = [
        ("What", "What is {keyword}?", "Define or explain {keyword}."),
        ("How", "How does {keyword} work?", "Explain the process or mechanism of {keyword}."),
        ("Why", "Why is {keyword} important?", "Explain the significance of {keyword}."),
        ("When", "When did {keyword} occur?", "Specify the time or period of {keyword}."),
        ("Where", "Where is {keyword} located?", "Identify the location or context of {keyword}.")
    ]
    
    # Strategy 1: Generate questions based on keywords with context
    for keyword in keywords:
        if len(questions) >= n_questions:
            break
        
        # Find sentence containing the keyword
        for i, sentence in enumerate(sentences):
            if i in used_sentences:
                continue
            
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, sentence, re.IGNORECASE):
                # Choose appropriate question template
                template_type = random.choice(question_templates)
                question_word, question_format, _ = template_type
                
                # Create question
                question_text = question_format.format(keyword=keyword)
                
                # Extract answer from sentence (use the sentence as context)
                # For short answer, the answer should be concise
                answer = _extract_answer_from_sentence(sentence, keyword)
                
                questions.append({
                    'question': question_text,
                    'answer': answer,
                    'context': sentence,
                    'type': 'short_answer'
                })
                used_sentences.add(i)
                break
    
    # Strategy 2: Generate questions based on entities
    entity_question_templates = {
        'PERSON': "Who is {entity} and what is their significance?",
        'ORG': "What is {entity}?",
        'GPE': "Where is {entity} located and what is its importance?",
        'DATE': "What happened in {entity}?",
        'EVENT': "What is the {entity} event about?",
        'PRODUCT': "What is {entity}?"
    }
    
    for entity in entities:
        if len(questions) >= n_questions:
            break
        
        # Find sentence containing the entity
        for i, sentence in enumerate(sentences):
            if i in used_sentences:
                continue
            
            if entity['text'] in sentence:
                # Get appropriate question template for entity type
                question_template = entity_question_templates.get(
                    entity['label'], 
                    "What is {entity}?"
                )
                question_text = question_template.format(entity=entity['text'])
                
                # Use the sentence as the answer
                answer = sentence
                
                questions.append({
                    'question': question_text,
                    'answer': answer,
                    'context': sentence,
                    'type': 'short_answer'
                })
                used_sentences.add(i)
                break
    
    return questions[:n_questions]


def _extract_answer_from_sentence(sentence, keyword):
    """
    Helper function to extract a concise answer from a sentence.
    Tries to get the phrase containing the keyword plus surrounding context.
    """
    # Split sentence into words
    words = sentence.split()
    
    # Find the keyword position
    keyword_lower = keyword.lower()
    keyword_index = -1
    
    for i, word in enumerate(words):
        if keyword_lower in word.lower():
            keyword_index = i
            break
    
    if keyword_index == -1:
        # If keyword not found as single word, return full sentence
        return sentence
    
    # Extract context window around keyword (3 words before and after)
    start = max(0, keyword_index - 3)
    end = min(len(words), keyword_index + 4)
    
    answer_words = words[start:end]
    answer = ' '.join(answer_words)
    
    # Clean up and ensure proper sentence structure
    if not answer.endswith('.'):
        answer += '.'
    
    # If answer is too short, return full sentence
    if len(answer.split()) < 5:
        return sentence
    
    return answer
