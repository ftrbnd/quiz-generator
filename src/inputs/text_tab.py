import random
from phases.quiz_generation import generate_fill_blank_questions
import gradio as gr

current_quiz_state = {
    'questions': [],
    'num_questions': 0,
    'question_types': []
}

def format_quiz_markdown(questions: list, num_questions: int):
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

def generate_quiz_from_text(input: str, num_questions: int, question_types: list):
    global current_quiz_state

    if not input.strip():
        return "Please provide text to generate questions from."
    
    questions = generate_fill_blank_questions(input, num_questions)

    current_quiz_state['questions'] = questions
    current_quiz_state['num_questions'] = num_questions
    current_quiz_state['question_types'] = question_types

    md = format_quiz_markdown(questions, num_questions)
    return (
        gr.update(visible=True),
        gr.Markdown(md)
    )

def shuffle_quiz():
    global current_quiz_state
    
    if not current_quiz_state['questions']:
        return "Please generate a quiz first before shuffling!"
    
    shuffled_questions = current_quiz_state['questions'].copy()
    random.shuffle(shuffled_questions)
    
    md=format_quiz_markdown(shuffled_questions, current_quiz_state['num_questions'])
    return (
        gr.update(visible=True),
        gr.Markdown(md)
    )

def download_quiz():
    global current_quiz_state
    md = format_quiz_markdown(current_quiz_state['questions'], current_quiz_state['num_questions'])

    filename = "generated_quiz.md"
    with open(filename, "w") as f:
        f.write(md)
    return (filename, gr.Markdown(md))


def render():
    with gr.Tab("Text (prompt)"):
        with gr.Row():
            with gr.Column():
                text_input = gr.Textbox(
                    label="Input Text",
                    placeholder="Enter a prompt",
                    lines=12
                )
                num_questions = gr.Slider(
                    minimum=3,
                    maximum=15,
                    value=5,
                    step=1,
                    label="Number of Questions"
                )
                question_types = gr.CheckboxGroup(["Multiple choice", "True/false", "Short answer", "Open-ended", "Fill in the blank"], label="Question types", show_select_all=True)

                with gr.Row():
                    generate_button = gr.Button("Generate", variant="primary")
                    shuffle_button = gr.Button("Shuffle", variant="secondary")
            
            with gr.Column():
                download_button = gr.DownloadButton("Download", visible=False)
                text_output = gr.Markdown(label="Generated Quiz")
        
        generate_button.click(
            fn=generate_quiz_from_text,
            inputs=[text_input, num_questions,question_types],
            outputs=[download_button, text_output]
        )
        shuffle_button.click(
            fn=shuffle_quiz,
            inputs=[],
            outputs=[download_button, text_output]
        )
        download_button.click(
            fn=download_quiz,
            outputs=[download_button, text_output]
        )