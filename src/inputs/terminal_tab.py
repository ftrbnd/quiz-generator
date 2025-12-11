import gradio as gr
from terminal.difficulty import run_quiz as run_difficulty
from terminal.shuffle import run_quiz as run_shuffle
from terminal.question_pools import run_question_pools
from terminal.question_tags import run_question_tags

def render():
    with gr.Tab("Run from terminal"):
         with gr.Row():
            with gr.Column():
                button_13 = gr.Button("Set question difficulty (13)", variant="primary")
                button_60 = gr.Button("Shuffle questions (60)", variant="primary")
            with gr.Column():
                button_22 = gr.Button("Question pools (22)", variant="primary")
                button_43 = gr.Button("Question tags (43)", variant="primary")

    button_13.click(
        fn=run_difficulty,
    )
    button_60.click(
        fn=run_shuffle,
    )
    button_22.click(
        fn=run_question_pools,
    )
    button_43.click(
        fn=run_question_tags,
    )