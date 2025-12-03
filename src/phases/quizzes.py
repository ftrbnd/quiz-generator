import random
import gradio as gr
from phases.question_types import generate_fill_blank_questions

class Quiz:
    def __init__(self):
        self.current_quiz_state = {
            'questions': [],
            'num_questions': 0,
            'question_types': []
        }

    def generate_from_text(self, input: str, num_questions: int, question_types: list):
        if not input.strip():
            return "Please provide text to generate questions from."
        
        questions = generate_fill_blank_questions(input, num_questions)

        self.current_quiz_state['questions'] = questions
        self.current_quiz_state['num_questions'] = num_questions
        self.current_quiz_state['question_types'] = question_types

        md = self.format_markdown(questions, num_questions)
        return (
            gr.update(visible=True),
            gr.Markdown(md)
        )

    def shuffle(self):
        if not self.current_quiz_state['questions']:
            return "Please generate a quiz first before shuffling!"
        
        shuffled_questions = self.current_quiz_state['questions'].copy()
        random.shuffle(shuffled_questions)
        
        md=self.format_markdown(shuffled_questions, self.current_quiz_state['num_questions'])
        return (
            gr.update(visible=True),
            gr.Markdown(md)
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
        md = self.format_markdown(self.current_quiz_state['questions'], self.current_quiz_state['num_questions'])

        filename = "generated_quiz.md"
        with open(filename, "w") as f:
            f.write(md)
        return (filename, gr.Markdown(md))
