import gradio as gr
from src.phases.quizzes import Quiz

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
                question_types = gr.CheckboxGroup([
                        ("Multiple choice", "mcq"),
                        ("Fill in the blank", "fill_blank"),
                        ("True/False", "t/f"),
                        ("Short answer", "short_answer")
                    ],
                    value="mcq",
                    label="Question types", 
                    show_select_all=True
                )

                with gr.Row():
                    generate_button = gr.Button("Generate", variant="primary")
                    llm_button = gr.Button("✨ Generate with AI",variant="primary")
                    shuffle_button = gr.Button("Shuffle", variant="secondary")
            
            with gr.Column():
                text_output = gr.Markdown(label="Generated Quiz")
                file_type_radio = gr.Radio(["csv", "md", "pdf", "txt"], label="File type")
                with gr.Row():
                    download_button = gr.DownloadButton("Download", visible=False)
                    analyze_button = gr.Button("Analyze", visible=False, variant="secondary")
        
        generate_button.click(
            fn=lambda text, num, types: quiz.generate("text", text, num, types),
            inputs=[text_input, num_questions, question_types],
            outputs=[download_button, analyze_button, text_output]
        )
        llm_button.click(
            fn=lambda text, num, types: quiz.generate("ai", text, num, types),
            inputs=[text_input, num_questions, question_types], 
            outputs=[download_button, analyze_button, text_output]
        )
        shuffle_button.click(
            fn=quiz.shuffle,
            inputs=[],
            outputs=[download_button, analyze_button, text_output]
        )
        download_button.click(
            fn=quiz.download,
            inputs=[file_type_radio],
            outputs=[download_button, text_output]
        )
        analyze_button.click(
            fn=quiz.analyze,
            outputs=[download_button, analyze_button, text_output]
        )