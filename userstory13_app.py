import random
import gradio as gr


QUESTIONS = [
    # EASY (6 questions)
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4",
        "difficulty": "easy",
    },
    {
        "question": "What color is a banana?",
        "options": ["Red", "Yellow", "Blue", "Purple"],
        "answer": "Yellow",
        "difficulty": "easy",
    },
    {
        "question": "Which animal barks?",
        "options": ["Cat", "Dog", "Cow", "Bird"],
        "answer": "Dog",
        "difficulty": "easy",
    },
    {
        "question": "What color is the sky on a clear, sunny day?",
        "options": ["Blue", "Green", "Orange", "Pink"],
        "answer": "Blue",
        "difficulty": "easy",
    },
    {
        "question": "How many days are in a week?",
        "options": ["5", "6", "7", "8"],
        "answer": "7",
        "difficulty": "easy",
    },
    {
        "question": "Which one is a fruit?",
        "options": ["Carrot", "Potato", "Apple", "Broccoli"],
        "answer": "Apple",
        "difficulty": "easy",
    },

    # MEDIUM (6 questions)
    {
        "question": "What is 12 × 8?",
        "options": ["96", "88", "108", "86"],
        "answer": "96",
        "difficulty": "medium",
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": [
            "Charles Dickens",
            "William Shakespeare",
            "Mark Twain",
            "J.K. Rowling"
        ],
        "answer": "William Shakespeare",
        "difficulty": "medium",
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Mars", "Earth", "Venus", "Jupiter"],
        "answer": "Mars",
        "difficulty": "medium",
    },
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": "Paris",
        "difficulty": "medium",
    },
    {
        "question": "What is the square root of 81?",
        "options": ["7", "8", "9", "10"],
        "answer": "9",
        "difficulty": "medium",
    },
    {
        "question": "Which gas do plants primarily absorb for photosynthesis?",
        "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Hydrogen"],
        "answer": "Carbon Dioxide",
        "difficulty": "medium",
    },

    # HARD (6 questions)
    {
        "question": "What is the derivative of x²?",
        "options": ["x", "2x", "x²", "2"],
        "answer": "2x",
        "difficulty": "hard",
    },
    {
        "question": "Which data structure uses LIFO?",
        "options": ["Queue", "Stack", "Array", "Tree"],
        "answer": "Stack",
        "difficulty": "hard",
    },
    {
        "question": "What is the time complexity of binary search?",
        "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"],
        "answer": "O(log n)",
        "difficulty": "hard",
    },
    {
        "question": "In Big-O notation, what is the time complexity of bubble sort in the average case?",
        "options": ["O(n)", "O(log n)", "O(n²)", "O(n log n)"],
        "answer": "O(n²)",
        "difficulty": "hard",
    },
    {
        "question": "Which of the following is NOT a primary OOP concept?",
        "options": ["Encapsulation", "Polymorphism", "Recursion", "Inheritance"],
        "answer": "Recursion",
        "difficulty": "hard",
    },
    {
        "question": "Which protocol is used to securely transfer web pages over the internet?",
        "options": ["HTTP", "FTP", "SMTP", "HTTPS"],
        "answer": "HTTPS",
        "difficulty": "hard",
    },
]


def shuffle_answers(question):
    """Return a copy of question with shuffled options."""
    q = question.copy()
    shuffled = q["options"][:]
    random.shuffle(shuffled)
    q["options"] = shuffled
    return q


def generate_quiz(difficulty, num_questions):
    """
    Filter by difficulty and return up to num_questions,
    with answers shuffled.
    """
    filtered = [q for q in QUESTIONS if q["difficulty"] == difficulty]
    selected = random.sample(filtered, min(num_questions, len(filtered)))
    return [shuffle_answers(q) for q in selected]




def start_quiz(difficulty, num_q):
    num_q = int(num_q)
    quiz = generate_quiz(difficulty, num_q)

    if not quiz:
        return (
            "No questions available for this difficulty.",
            gr.update(choices=[], value=None),
            "",
            "Score: 0 / 0",
            None,
        )

    state = {
        "difficulty": difficulty,
        "quiz": quiz,
        "index": 0,
        "score": 0,
        "requested": num_q,
    }

    q = quiz[0]
    first_msg = (
        f"Loaded **{len(quiz)}** question(s) for **{difficulty}** "
        f"(you requested {num_q}).\n\n"
        f"**Q1. {q['question']}**"
    )

    return (
        first_msg,
        gr.update(choices=q["options"], value=None),
        "Select your answer and click Submit.",
        "Score: 0 / 0",
        state,
    )


def submit_answer(selected, state):
    # No quiz started yet
    if state is None or "quiz" not in state:
        return (
            "Click **Start Quiz** to begin.",
            gr.update(choices=[], value=None),
            "",
            "Score: 0 / 0",
            state,
        )

    quiz = state["quiz"]
    idx = state["index"]
    score = state["score"]

    # No answer selected – do not advance
    if selected is None:
        q = quiz[idx]
        return (
            f"**Q{idx+1}. {q['question']}**",
            gr.update(choices=q["options"], value=None),
            "⚠️ Please select an answer before submitting.",
            f"Score: {score} / {idx}",
            state,
        )

    current_q = quiz[idx]
    correct = current_q["answer"]

    if selected == correct:
        score += 1
        feedback = "✅ Correct!"
    else:
        feedback = f"❌ Wrong! Correct answer: **{correct}**"

    idx += 1
    state["index"] = idx
    state["score"] = score

    # Finished quiz
    if idx >= len(quiz):
        final_msg = (
            f"### Quiz Complete!\n\n"
            f"You answered **{len(quiz)}** question(s).\n\n"
            f"Your final score: **{score} / {len(quiz)}**"
        )
        return (
            final_msg,
            gr.update(choices=[], value=None),
            feedback,
            f"Final Score: {score} / {len(quiz)}",
            state,
        )

    # Next question
    next_q = quiz[idx]
    question_text = f"**Q{idx+1}. {next_q['question']}**"
    return (
        question_text,
        gr.update(choices=next_q["options"], value=None),  # ✅ fixed here
        feedback,
        f"Score: {score} / {idx}",
        state,
    )




with gr.Blocks() as demo:
    gr.Markdown("# 🧠 Interactive Quiz App")
    gr.Markdown(
        "Each difficulty has **6 questions**.\n\n"
        "1. Select a difficulty\n"
        "2. Choose how many questions (1–6)\n"
        "3. Click **Start Quiz**\n"
        "4. For each question: pick an answer and click **Submit Answer**"
    )

    with gr.Row():
        difficulty_radio = gr.Radio(
            ["easy", "medium", "hard"],
            label="Select Difficulty",
            value="easy",
        )
        num_questions_slider = gr.Slider(
            1,
            6,
            value=3,
            step=1,
            label="Number of Questions",
        )

    start_btn = gr.Button("Start Quiz")
    submit_btn = gr.Button("Submit Answer")

    question_md = gr.Markdown("Click **Start Quiz** to begin.")
    answer_options = gr.Radio([], label="Answer Options")
    feedback_md = gr.Markdown("")
    score_md = gr.Markdown("Score: 0 / 0")

    quiz_state = gr.State()

    start_btn.click(
        start_quiz,
        inputs=[difficulty_radio, num_questions_slider],
        outputs=[question_md, answer_options, feedback_md, score_md, quiz_state],
    )

    submit_btn.click(
        submit_answer,
        inputs=[answer_options, quiz_state],
        outputs=[question_md, answer_options, feedback_md, score_md, quiz_state],
    )


if __name__ == "__main__":
    demo.launch()
