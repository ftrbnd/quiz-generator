import gradio as gr
from phases.quiz_generator import QuizAI   

def render():
    quiz_ai = QuizAI()

    def process_document(file):
        if file is None:
            return "Please upload a file.", ""
        msg = quiz_ai.upload_document(file.name)
        return msg, quiz_ai.detect_material()
    

    def explain_answer(quiz_text):
        if not quiz_text.strip():
            return "No quiz text found. Generate questions first."
        return quiz_ai.generate_explanations(quiz_text)

    with gr.Tab("Generate Quiz with Explanations"):

        file_input = gr.File(label="Upload .txt file")
        upload_btn = gr.Button("Upload Document")
        upload_status = gr.Textbox(label="Upload Status")
        keywords_output = gr.Textbox(label="Detected Keywords")

        upload_btn.click(
            process_document,
            inputs=file_input,
            outputs=[upload_status, keywords_output]
        )

        quiz_btn = gr.Button("Generate Quiz")
        quiz_output = gr.Textbox(label="Generated Quiz", lines=12)
        quiz_btn.click(quiz_ai.generate_quiz, outputs=quiz_output)

        explain_btn = gr.Button("Explain Answer")
        explanation_output = gr.Textbox(label="Explanation", lines=8)
        explain_btn.click(
            explain_answer,
            inputs=quiz_output,
            outputs=explanation_output
        )