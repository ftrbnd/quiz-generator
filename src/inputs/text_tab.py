import gradio as gr
from phases.quizzes import Quiz

def render():
    quiz = Quiz()

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
            fn=quiz.generate_from_text,
            inputs=[text_input, num_questions,question_types],
            outputs=[download_button, text_output]
        )
        shuffle_button.click(
            fn=quiz.shuffle,
            inputs=[],
            outputs=[download_button, text_output]
        )
        download_button.click(
            fn=quiz.download,
            outputs=[download_button, text_output]
        )