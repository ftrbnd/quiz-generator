import gradio as gr
import inputs.text_tab as text_tab
import inputs.file_tab as file_tab

with gr.Blocks(title="Automatic Quiz Generator") as demo:
    gr.Markdown("""
        # Automatic Quiz Generator  
        Use the **Text** or **File** tab below to enter content, then generate a quiz automatically.
    """)
    with gr.Tabs():
        text_tab.render()
        file_tab.render()

if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), share=True)
