import random
import gradio as gr
from . import question_types as q_types
from . import algorithms

class Quiz:
    def __init__(self):
        self.input_text = ''
        self.markdown_result = ''
        self.current_quiz_state = {
            'questions': [],
            'num_questions': 0,
            'question_types': []
        }

    def generate_from_text(self, input: str, num_questions: int, question_types: list):
        if not input.strip():
            return (
                gr.update(visible=False),
                gr.update(visible=False),
                "Please provide text to generate questions from."
            )
        if not question_types:
            return (
                gr.update(visible=False),
                gr.update(visible=False),
                "Please select at least one question type."
            )
        
        all_questions = []
        questions_per_type = num_questions // len(question_types)
        remainder = num_questions % len(question_types)

        for i, q_type in enumerate(question_types):
            # Add extra question to first types if there's a remainder
            count = questions_per_type + (1 if i < remainder else 0)
            
            if count > 0:
                if q_type == 'fill_blank':
                    questions = q_types.generate_fill_blank_questions(input, count)
                elif q_type == 'mcq':
                    questions = q_types.generate_mcq_questions(input, count)
                elif q_type == 'topic':
                    questions = q_types.generate_topic_questions(input, count)
                else:
                    continue
                
                all_questions.extend(questions)

        self.input_text = input
        self.current_quiz_state['questions'] = all_questions
        self.current_quiz_state['num_questions'] = len(all_questions)
        self.current_quiz_state['question_types'] = question_types

        self.markdown_result = self.format_markdown(all_questions, len(all_questions))
        return (
            gr.update(visible=True),
            gr.update(visible=True),
            gr.Markdown(self.markdown_result)
        )

    def shuffle(self):
        if not self.current_quiz_state['questions']:
            return (
                gr.update(visible=False),
                gr.update(visible=False),
                "Please generate a quiz first before shuffling!"
            )
        
        shuffled_questions = self.current_quiz_state['questions'].copy()
        random.shuffle(shuffled_questions)
        
        self.markdown_result = self.format_markdown(shuffled_questions, self.current_quiz_state['num_questions'])
        return (
            gr.update(visible=True),
            gr.update(visible=True),
            gr.Markdown(self.markdown_result)
        )
    
    def format_markdown(self, questions: list, num_questions: int):
        """Format given questions into markdown, as a string"""
        if not questions:
            return "# Generated Quiz (0 questions)\n\nNo questions generated."
        
        # Group questions by type
        questions_by_type = {}
        for q in questions:
            q_type = q.get('type', 'unknown')
            if q_type not in questions_by_type:
                questions_by_type[q_type] = []
            questions_by_type[q_type].append(q)
        
        output = f"\n\n# Generated Quiz ({num_questions} questions)\n\n"
        
        type_titles = {
            'fill_blank': '## Fill in the Blank Questions',
            'mcq': '## Multiple Choice Questions',
            'topic': '## Topic Questions',
        }
        
        question_number = 1
        for q_type, type_questions in questions_by_type.items():
            if type_questions:
                output += f"{type_titles.get(q_type, '## Questions')}\n\n"
                
                for q in type_questions:
                    output += f"**Q{question_number}.** {q['question']}\n\n"
                    
                    # Format based on question type
                    if q_type == 'multiple_choice' and 'options' in q:
                        for option in q['options']:
                            output += f"   {option}\n"
                        output += f"\n*Answer: {q['answer']}*\n\n"
                    elif q_type == 'true_false':
                        output += f"*Answer: {q['answer']}*\n\n"
                    elif q_type in ['fill_blank', 'short_answer', 'open_ended']:
                        output += f"*Answer: {q['answer']}*\n\n"
                    
                    question_number += 1
                
                output += "\n"
        
        return output



    def download(self):
        filename = "generated_quiz.md"
        with open(filename, "w") as f:
            f.write(self.markdown_result)
        return (
            filename,
            gr.update(visible=True),
            gr.Markdown(self.markdown_result)
        )
    
    def analyze(self):
        analysis = "\n---\n## Analysis\n\n"
    
        keywords = algorithms.extract_keywords_tfidf(self.input_text, top_n=10)
        analysis += f"**Key Terms (TF-IDF):** {', '.join(keywords)}\n\n"
        
        entities = algorithms.extract_entities_ner(self.input_text)
        if entities:
            analysis += f"**Named Entities (NER):** "
            entity_strs = [f"{e['text']} ({e['label']})" for e in entities[:10]]
            analysis += ', '.join(entity_strs) + "\n\n"
        
        topics = algorithms.extract_topics_lda(self.input_text, n_topics=3)
        if topics:
            analysis += "**Topics (LDA):**\n"
            for i, topic in enumerate(topics, 1):
                analysis += f"   Topic {i}: {', '.join(topic[:5])}\n"

        self.markdown_result += analysis

        return (
            gr.update(visible=True),
            gr.update(visible=True),
            gr.Markdown(self.markdown_result)
        )
