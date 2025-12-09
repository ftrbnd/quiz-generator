import csv
from io import StringIO
import random
import re
import gradio as gr
from . import question_types as q_types
from . import algorithms
from . import llm_client
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

class Quiz:
    def __init__(self):
        self.input_text = ''
        self.markdown_result = ''
        self.current_quiz_state = {
            'questions': [],
            'num_questions': 0,
            'question_types': []
        }

    def generate_with_ai(self, input: str, num_questions: int, question_types: list):
        if not input or not input.strip():
            return (
                    gr.update(visible=False),
                    gr.update(visible=False),
                    "Please provide text to generate questions from."
                )
        try:
            result = llm_client.generate_from_llm(
                source_text=input,
                num_questions=num_questions,
                question_types=question_types
            )
            self.markdown_result = result
            self.input_text = input
            # TODO: extract questions from Groq response
            # self.current_quiz_state['questions'] = all_questions
            # self.current_quiz_state['num_questions'] = len(all_questions)
            self.current_quiz_state['question_types'] = question_types

            show_buttons = "0 questions" not in self.markdown_result
            return (
                gr.update(visible=show_buttons),
                gr.update(visible=show_buttons),
                gr.Markdown(self.markdown_result)
            )
        except Exception as e:
            return (
                gr.update(visible=False),
                gr.update(visible=False),
                f"**Error calling Groq API:** {e}"
            )

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
                elif q_type == 't/f':
                    questions = q_types.generate_true_false_questions(input, count)
                elif q_type == "short_answer":
                    questions = q_types.generate_short_answer_questions(input, count)
                else:
                    continue
                
                all_questions.extend(questions)

        self.input_text = input
        self.current_quiz_state['questions'] = all_questions
        self.current_quiz_state['num_questions'] = len(all_questions)
        self.current_quiz_state['question_types'] = question_types

        self.markdown_result = self.format_markdown(all_questions, len(all_questions))

        show_buttons = "0 questions" not in self.markdown_result
        return (
            gr.update(visible=show_buttons),
            gr.update(visible=show_buttons),
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

        show_buttons = "0 questions" not in self.markdown_result
        return (
            gr.update(visible=show_buttons),
            gr.update(visible=show_buttons),
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
            'fill_blank': '## Fill in the blank Questions',
            'mcq': '## Multiple choice Questions',
            't/f': '## True/false Questions',
            'short_answer': '## Short answer Questions',
        }
        
        # format the questions by question type
        question_number = 1
        for q_type, type_questions in questions_by_type.items():
            if type_questions:
                output += f"{type_titles.get(q_type, '## Questions')}\n\n"
                
                for q in type_questions:
                    output += f"**Q{question_number}.** {q['question']}\n\n"
                    
                    # Format based on question type
                    if q_type == 'mcq' and 'options' in q:
                        for option in q['options']:
                            output += f"\n- {option}"
                        output += f"\n\n*Answer: {q['answer']}*\n\n"
                    elif q_type == 'topic':
                        output += f"*Answer: {q['answer']}*\n\n"
                    elif q_type in ['fill_blank', 'short_answer', 't/f']:
                        output += f"*Answer: {q['answer']}*\n\n"
                    
                    question_number += 1
                
                output += "\n"
        
        return output

    def format_as_csv(self, questions: list):
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Question Number', 'Type', 'Question', 'Answer', 'Options'])
        
        # Write questions
        for i, q in enumerate(questions, 1):
            q_type = q.get('type', 'unknown')
            question_text = q.get('question', '')
            answer = q.get('answer', '')
            
            # Handle options for multiple choice
            options = ''
            if 'options' in q:
                options = ' | '.join(q['options'])
            
            writer.writerow([i, q_type, question_text, answer, options])
        
        return output.getvalue()
    
    def format_as_txt(self, questions: list):
        if not questions:
            return "Generated Quiz (0 questions)\n\nNo questions generated."
        
        output = f"Generated Quiz ({len(questions)} questions)\n"
        output += "=" * 70 + "\n\n"
        
        question_number = 1
        for q in questions:
            q_type = q.get('type', 'unknown').replace('_', ' ').title()
            output += f"Q{question_number}. [{q_type}]\n"
            output += f"{q['question']}\n\n"
            
            if 'options' in q:
                for option in q['options']:
                    output += f"   {option}\n"
                output += "\n"
            
            output += f"Answer: {q['answer']}\n"
            output += "-" * 70 + "\n\n"
            question_number += 1
        
        return output

    def format_as_pdf(self, questions: list, filename: str):
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2C3E50',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor='#34495E',
            spaceAfter=12,
            spaceBefore=20
        )
        
        question_style = ParagraphStyle(
            'Question',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            leftIndent=0
        )
        
        option_style = ParagraphStyle(
            'Option',
            parent=styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=3
        )
        
        answer_style = ParagraphStyle(
            'Answer',
            parent=styles['Normal'],
            fontSize=11,
            textColor='#27AE60',
            spaceAfter=15,
            leftIndent=20
        )
        
        title = Paragraph(f"Generated Quiz ({len(questions)} questions)", title_style)
        story.append(title)
        story.append(Spacer(1, 0.3 * inch))
        
        # Group questions by type
        questions_by_type = {}
        for q in questions:
            q_type = q.get('type', 'unknown')
            if q_type not in questions_by_type:
                questions_by_type[q_type] = []
            questions_by_type[q_type].append(q)
        
        type_titles = {
            'fill_blank': 'Fill in the Blank Questions',
            'mcq': 'Multiple Choice Questions',
            'topic': 'Topic Questions',
        }
        
        question_number = 1
        
        for q_type, type_questions in questions_by_type.items():
            if type_questions:
                # Add section heading
                section_title = type_titles.get(q_type, 'Questions')
                heading = Paragraph(section_title, heading_style)
                story.append(heading)
                story.append(Spacer(1, 0.1 * inch))
                
                for q in type_questions:
                    # Clean HTML/markdown from question text
                    question_text = self._clean_text_for_pdf(q['question'])
                    
                    # Add question
                    question_para = Paragraph(
                        f"<b>Q{question_number}.</b> {question_text}",
                        question_style
                    )
                    story.append(question_para)
                    story.append(Spacer(1, 0.05 * inch))
                    
                    # Add options if multiple choice
                    if 'options' in q:
                        for option in q['options']:
                            option_text = self._clean_text_for_pdf(option)
                            option_para = Paragraph(option_text, option_style)
                            story.append(option_para)
                        story.append(Spacer(1, 0.05 * inch))
                    
                    # Add answer
                    answer_text = self._clean_text_for_pdf(q['answer'])
                    answer_para = Paragraph(f"<i>Answer: {answer_text}</i>", answer_style)
                    story.append(answer_para)
                    story.append(Spacer(1, 0.15 * inch))
                    
                    question_number += 1
        
        doc.build(story)
        return filename

    def _clean_text_for_pdf(self, text):
        """Escape special characters"""
        if not text:
            return ""
        
        # Replace common markdown/HTML with plain text
        text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)  # Bold
        text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)      # Italic
        text = re.sub(r'_____', '___________', text)          # Blanks
        
        # Escape XML special characters for ReportLab
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        # Restore bold/italic tags
        text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
        
        return text

    def download(self, file_type: str):
        """Download quiz in the specified file format"""
        questions = self.current_quiz_state['questions']
        
        if not questions:
            return (
                None,
                gr.Markdown("No quiz to download. Please generate a quiz first.")
            )
        file_type = "md" if file_type not in ["csv", "md", "pdf", "txt"] else file_type
        filename = f"generated_quiz.{file_type}"
        try:
            if file_type == "csv":
                content = self.format_as_csv(questions)
                with open(filename, "w", encoding='utf-8', newline='') as f:
                    f.write(content)
                    
            elif file_type == "txt":
                content = self.format_as_txt(questions)
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(content)
                    
            elif file_type == "pdf":
                filename = self.format_as_pdf(questions, filename)
                
            else:
                content = self.markdown_result
                with open(filename, "w", encoding='utf-8') as f:
                    f.write(content)
            
            return (
                filename,
                gr.Markdown(f"{self.markdown_result}\n\nQuiz downloaded as **{filename}**\n\n")
            )
            
        except Exception as e:
            return (
                None,
                gr.Markdown(f"Error downloading quiz: {str(e)}\n\n{self.markdown_result}")
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
