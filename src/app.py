import gradio as gr
from inputs import text_tab
from inputs import file_tab
from phases.quiz_generator import QuizAI   

# -------- GLOBAL CSS (affects root HTML, not internal components) --------
global_css = """
/* Background: deep AI gradient */
body, html {
    background: linear-gradient(135deg, #041833 0%, #071e42 40%, #0a244f 100%) !important;
    font-family: 'Inter', sans-serif !important;
    color: #e9eef7 !important;
}

/* Remove Gradio footer */
footer, .gradio-container footer {
    display: none !important;
}

* { transition: all 0.25s ease-in-out; }
"""

# -------- SHADOW-DOM CSS (applies to actual Gradio components) --------
shadow_dom_css = """
<script>
function applyCustomStyles() {
    const app = document.querySelector("gradio-app");
    if (!app) return;

    const shadow = app.shadowRoot;
    if (!shadow) return;

    const styleTag = document.createElement("style");
    styleTag.textContent = `
        /* ---------- Tabs ---------- */
        .tab-nav button {
            background: rgba(255,255,255,0.06) !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: #dfe8f6 !important;
            border-radius: 10px !important;
            padding: 8px 16px !important;
        }
        .tab-nav button.selected {
            background: rgba(255,255,255,0.16) !important;
            color: white !important;
        }

        /* ---------- Text Inputs ---------- */
        textarea, input, select {
            background: rgba(255,255,255,0.08) !important;
            border-radius: 12px !important;
            border: 1px solid rgba(255,255,255,0.18) !important;
            color: #dde6f9 !important;
            padding: 12px !important;
            font-size: 15px !important;
        }

        /* ---------- Buttons ---------- */
        button {
            background: linear-gradient(135deg, #1b56d9, #4b72ff) !important;
            border-radius: 12px !important;
            color: #fff !important;
            padding: 12px 20px !important;
            border: none !important;
            font-size: 16px !important;
            box-shadow: 0 0 15px rgba(40,120,255,0.45) !important;
        }
        button:hover {
            background: linear-gradient(135deg, #2c67ff, #6c89ff) !important;
            box-shadow: 0 0 22px rgba(70,140,255,0.7) !important;
            transform: translateY(-1px);
        }

        /* ---------- Panels / Blocks ---------- */
        .block, .panel, .row, .group {
            backdrop-filter: blur(18px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(18px) saturate(180%) !important;
            background: rgba(255,255,255,0.05) !important;
            border-radius: 18px !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            padding: 20px !important;
        }

        /* ---------- Markdown ---------- */
        h1, h2, h3, p {
            color: #eaf1ff !important;
        }
    `;

    shadow.appendChild(styleTag);
}

setTimeout(applyCustomStyles, 600);
</script>
"""

# ------------------------------
# Quiz AI Generator
# ------------------------------
quiz_ai = QuizAI()

def process_document(file):
    if file is None:
        return "Please upload a file.", ""
    msg = quiz_ai.upload_document(file.name)
    return msg, quiz_ai.detect_material()

def generate_quiz():
    return quiz_ai.generate_quiz()

def explain_answer(quiz_text):
    if not quiz_text.strip():
        return "No quiz text found. Generate questions first."
    return quiz_ai.generate_explanations(quiz_text)

# --------------------------------------------------------------------------
#                           MAIN GRADIO APP
# --------------------------------------------------------------------------

with gr.Blocks(title="Automatic Quiz Generator") as demo:

    gr.HTML(f"<style>{global_css}</style>")
    gr.HTML(shadow_dom_css)

    gr.Markdown("""
        # Automatic Quiz Generator  
        Enter text or upload a file to generate custom quizzes using AI.
    """)

    with gr.Tabs():
        text_tab.render()
        file_tab.render()

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
            quiz_btn.click(generate_quiz, outputs=quiz_output)

            explain_btn = gr.Button("Explain Answer")
            explanation_output = gr.Textbox(label="Explanation", lines=8)
            explain_btn.click(
                explain_answer,
                inputs=quiz_output,
                outputs=explanation_output
            )

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), share=True)
