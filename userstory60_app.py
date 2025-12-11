import random
import gradio as gr


QUESTIONS = [
   
    {
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "6"],
        "answer": "4",
        "difficulty": "easy",
    },
    {
        "question": "What color is the sky on a clear day?",
        "options": ["Red", "Blue", "Green", "Yellow"],
        "answer": "Blue",
        "difficulty": "easy",
    },
   
    {
        "question": "How many days are there in a week?",
        "options": ["5", "6", "7", "8"],
        "answer": "7",
        "difficulty": "easy",
    },
    {
        "question": "Which one is a fruit?",
        "options": ["Carrot", "Potato", "Apple", "Onion"],
        "answer": "Apple",
        "difficulty": "easy",
    },
    {
        "question": "What color are most grass fields?",
        "options": ["Blue", "Green", "Red", "Purple"],
        "answer": "Green",
        "difficulty": "easy",
    },

   
    {
        "question": "What is 12 × 8?",
        "options": ["96", "88", "108", "86"],
        "answer": "96",
        "difficulty": "medium",
    },
    {
        "question": "Who wrote 'Romeo and Juliet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Mark Twain", "J.K. Rowling"],
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
        "question": "In Big-O notation, what is the average time complexity of bubble sort?",
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
]


def shuffle_answers(question):
    """
    Takes a question dictionary and returns a new version
    where the answer choices are shuffled but the correct
    answer remains accurately mapped.
    """
    q = question.copy()
    shuffled_options = q["options"][:]
    random.shuffle(shuffled_options)

    # Answer stored as value (string), so no need to change it
    q["options"] = shuffled_options
    return q


def generate_quiz(difficulty: str, num_questions: int = 3):
    """
    Generate a quiz matching the chosen difficulty,
    with shuffled answer options for each question.
    """
    difficulty = difficulty.lower().strip()
    valid = {"easy", "medium", "hard"}

    if difficulty not in valid:
        raise ValueError("Invalid difficulty level")

    # Filter questions
    filtered = [q for q in QUESTIONS if q["difficulty"] == difficulty]

    # Limit number of questions
    num_questions = min(num_questions, len(filtered))

    # Randomly choose questions
    selected = random.sample(filtered, num_questions)

    # Shuffle answer options PER QUESTION
    return [shuffle_answers(q) for q in selected]




def build_quiz(difficulty, num_questions):
    try:
        n = int(num_questions)
        if n <= 0:
            return "❌ Number of questions must be positive."
    except ValueError:
        return "❌ Please enter a valid integer for number of questions."

    try:
        quiz = generate_quiz(difficulty, n)
    except ValueError as e:
        return f"❌ {e}"

    if not quiz:
        return "⚠️ No questions found for that difficulty."

    lines = []
    lines.append(
        f"### Your {difficulty.capitalize()} Quiz "
        f"({len(quiz)} question(s), requested {n})\n"
    )

    for i, q in enumerate(quiz, start=1):
        lines.append(f"**Q{i}. {q['question']}**")
        for idx, option in enumerate(q["options"], start=1):
            lines.append(f"{idx}. {option}")
        lines.append("")

    return "\n".join(lines)




with gr.Blocks() as demo:
    gr.Markdown("# 🧠 Simple Quiz Generator (Gradio)")
    gr.Markdown(
        "Updated so each level has **5 questions**.\n\n"
        "- Choose difficulty\n"
        "- Set how many questions you want (up to 5)\n"
        "- Options are shuffled for each question"
    )

    with gr.Row():
        diff_radio = gr.Radio(
            ["easy", "medium", "hard"],
            label="Choose Difficulty",
            value="easy",
        )
        num_input = gr.Slider(
            minimum=1,
            maximum=5,
            value=3,
            step=1,
            label="Number of questions",
        )

    generate_btn = gr.Button("Generate Quiz")
    output_md = gr.Markdown("👈 Choose options and click **Generate Quiz**.")

    generate_btn.click(
        build_quiz,
        inputs=[diff_radio, num_input],
        outputs=output_md,
    )


if __name__ == "__main__":
    demo.launch()
