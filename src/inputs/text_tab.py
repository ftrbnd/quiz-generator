from phases.quiz_generation import generate_fill_blank_questions
import gradio as gr

def generate_quiz_from_text(input: str, num_questions: int, question_types: list):
    if not input.strip():
        return "Please provide text to generate questions from."
    
    questions = generate_fill_blank_questions(input, num_questions)

    output = ""
    if questions:
        output += "## Fill in the Blank Questions\n\n"
        for i, q in enumerate(questions, 1):
            output += f"**Q{i}.** {q['question']}\n\n"
            output += f"*Answer: {q['answer']}*\n\n"

    return gr.Markdown(f"""
        \n\n# Generated Quiz ({num_questions} questions)
        \n\n{output}
        """)
    
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

                generate_button = gr.Button("Generate", variant="primary")
            
            with gr.Column():
                text_output = gr.Markdown(label="Generated Quiz")
        
        generate_button.click(
            fn=generate_quiz_from_text,
            inputs=[text_input, num_questions,question_types],
            outputs=text_output
        )