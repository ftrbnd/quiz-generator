# src/inputs/text_tab.py

import gradio as gr
from phases.llm_client import generate_quiz_from_text

def render():
    with gr.Tab("Text (prompt)"):
        # Input area
        prompt = gr.Textbox(
            lines=15,
            label="Paste or type your text here",
            placeholder="Enter text for quiz generation..."
        )
        num_q = gr.Slider(
            minimum=1, maximum=50, step=1, value=5,
            label="Number of questions"
        )
        q_types = gr.CheckboxGroup(
            choices=["Multiple choice", "Short answer", "True/False", "Fill in the blank"],
            value=[],
            label="Question types (optional)"
        )
        btn = gr.Button("Generate quiz")
        output = gr.Markdown()

        def on_click_generate(text, n, types):
            if not text or not text.strip():
                return "⚠️ Please provide some input text."
            try:
                result = generate_quiz_from_text(
                    source_text=text,
                    num_questions=n,
                    question_types=types
                )
                return result
            except Exception as e:
                return f"**Error calling Groq API:** {e}"

        btn.click(fn=on_click_generate, inputs=[prompt, num_q, q_types], outputs=output)
