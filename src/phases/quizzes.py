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
            return "Please provide text to generate questions from."
        
        questions = q_types.generate_fill_blank_questions(input, num_questions)

        self.input_text = input
        self.current_quiz_state['questions'] = questions
        self.current_quiz_state['num_questions'] = num_questions
        self.current_quiz_state['question_types'] = question_types

        self.markdown_result = self.format_markdown(questions, num_questions)
        return (
            gr.update(visible=True),
            gr.update(visible=True),
            gr.Markdown(self.markdown_result)
        )

    def shuffle(self):
        if not self.current_quiz_state['questions']:
            return "Please generate a quiz first before shuffling!"
        
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
        output = ""
        
        if questions:
            output += "## Fill in the Blank Questions\n\n"
            for i, q in enumerate(questions, 1):
                output += f"**Q{i}.** {q['question']}\n\n"
                output += f"*Answer: {q['answer']}*\n\n"
        
        return f"""
            \n\n# Generated Quiz ({num_questions} questions)
            \n\n{output}
            """


    def download(self):
        filename = "generated_quiz.md"
        with open(filename, "w") as f:
            f.write(self.markdown_result)
        return (filename, gr.Markdown(self.markdown_result))
    
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
