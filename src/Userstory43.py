import json
import random
import gradio as gr

# QUESTION POOLS (example) Userstory43
# Each pool represents one topic with multiple questions.

question_pools = {
    "Topic 1: NLP": [
        "What does NLP stand for?",
        "What is tokenization?",
        "Name one NLP application."
    ],
    "Topic 2: Machine Learning": [
        "What is supervised learning?",
        "Define overfitting.",
        "What is a dataset?"
    ],
    "Topic 3: Deep Learning": [
        "What is a neural network?",
        "Define activation function.",
        "What is backpropagation?"
    ]
}



# Generate quiz using question pools

def generate_quiz_from_pools(pools, settings):
    final_quiz = []

    for topic, questions in pools.items():
        amount = settings.get(topic, 0)

        # Avoid errors if amount > available questions
        amount = min(amount, len(questions))

        if amount > 0:
            chosen = random.sample(questions, amount)
            # Add topic label to each question (for clarity)
            for q in chosen:
                final_quiz.append(f"[{topic}] {q}")

    return final_quiz



# Save pool settings (quiz template)

def save_template(settings, filename="quiz_template.json"):
    with open(filename, "w") as f:
        json.dump(settings, f, indent=4)
    return f"Template saved as {filename}"


# Gradio interface callback

def create_quiz(selected_topics, questions_per_topic):
    """
    selected_topics: list of topics chosen by instructor
    questions_per_topic: integer (same number for each selected topic)
    """
    if not selected_topics:
        return "No topics selected.", ""

    # Build pool_settings dict based on UI input
    pool_settings = {topic: int(questions_per_topic) for topic in selected_topics}

    # Generate quiz
    selected_pools = {topic: question_pools[topic] for topic in selected_topics}
    quiz = generate_quiz_from_pools(selected_pools, pool_settings)

    if not quiz:
        return "No questions could be generated with the selected settings.", ""

    # Format quiz text nicely
    quiz_text_lines = []
    for i, q in enumerate(quiz, start=1):
        quiz_text_lines.append(f"{i}. {q}")
    quiz_text = "\n".join(quiz_text_lines)

    # Save template
    msg = save_template(pool_settings)

    return quiz_text, msg



# Build Gradio UI

with gr.Blocks() as demo:
    gr.Markdown("# Question Pools Quiz Generator")
    gr.Markdown(
        "Select topics and how many questions to draw from each topic. "
        "The system will create a quiz with equal coverage from each selected pool."
    )

    with gr.Row():
        topics_input = gr.CheckboxGroup(
            choices=list(question_pools.keys()),
            label="Select Topics (Question Pools)",
        )
        num_per_topic_input = gr.Slider(
            minimum=1,
            maximum=3,
            step=1,
            value=1,
            label="Questions per Topic"
        )

    generate_button = gr.Button("Generate Quiz")

    quiz_output = gr.Textbox(
        label="Generated Quiz",
        lines=10,
        interactive=False
    )

    template_output = gr.Textbox(
        label="Template Save Status",
        interactive=False
    )

    generate_button.click(
        fn=create_quiz,
        inputs=[topics_input, num_per_topic_input],
        outputs=[quiz_output, template_output],
    )


# Run the app

if __name__ == "__main__":
    demo.launch()
