# src/inputs/file_tab.py

import gradio as gr
from phases.llm_client import generate_quiz_from_text
import os

def render():
    with gr.Tab("Upload .txt file"):
        file_input = gr.File(
            file_count="single",
            file_types=[".txt"],
            label="Upload a .txt file"
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

        def on_click_generate(file_obj, n, types):
            if file_obj is None:
                return "⚠️ Please upload a .txt file."
            text = None
            # Handle different possible types of file_obj
            try:
                # If it's a file-like object (with read)
                if hasattr(file_obj, "read"):
                    raw = file_obj.read()
                    if isinstance(raw, (bytes, bytearray)):
                        text = raw.decode("utf-8", errors="ignore")
                    else:
                        text = raw  # assume str
                # If it's a str (filepath)
                elif isinstance(file_obj, str):
                    with open(file_obj, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()
                else:
                    return f"❗ Unsupported upload type: {type(file_obj)}"
            except Exception as e:
                return f"❗ Could not read file: {e}"
            if not text or not text.strip():
                return "⚠️ Uploaded file seems empty."

            try:
                return generate_quiz_from_text(
                    source_text=text,
                    num_questions=n,
                    question_types=types
                )
            except Exception as e:
                return f"**Error calling Groq API:** {e}"

        btn.click(fn=on_click_generate, inputs=[file_input, num_q, q_types], outputs=output)
