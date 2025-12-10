
import random

QUESTIONS = [
    # Easy questions
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
    # Medium questions
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
    # Hard questions
    {
        "question": "What is the derivative of x² with respect to x?",
        "options": ["x", "2x", "x²", "2"],
        "answer": "2x",
        "difficulty": "hard",
    },
    {
        "question": "Which data structure uses LIFO (Last In, First Out)?",
        "options": ["Queue", "Stack", "Array", "Tree"],
        "answer": "Stack",
        "difficulty": "hard",
    },
]


def generate_quiz(difficulty: str, num_questions: int = 3):
    """
    Generate a quiz with questions that match the requested difficulty.

    :param difficulty: 'easy', 'medium', or 'hard'
    :param num_questions: number of questions to return
    :return: list of questions (dicts)
    """
    difficulty = difficulty.lower().strip()
    valid_difficulties = {"easy", "medium", "hard"}

    if difficulty not in valid_difficulties:
        raise ValueError(f"Invalid difficulty '{difficulty}'. Must be one of {valid_difficulties}.")

    filtered_questions = [q for q in QUESTIONS if q["difficulty"] == difficulty]

    if not filtered_questions:
        raise ValueError(f"No questions found for difficulty '{difficulty}'.")

    # If there are fewer questions than requested, just return all of them
    num_questions = min(num_questions, len(filtered_questions))

    return random.sample(filtered_questions, num_questions)


def run_quiz():
    """
    Simple CLI to:
    1. Ask the student for difficulty.
    2. Generate the quiz based on that difficulty.
    3. Output the quiz questions to the console.
    """
    print("Welcome to the AI Quiz Generator!")
    print("Choose difficulty level: easy / medium / hard")

    while True:
        difficulty = input("Enter difficulty: ").strip().lower()
        try:
            quiz = generate_quiz(difficulty, num_questions=3)
            break
        except ValueError as e:
            print(e)
            print("Please try again.\n")

    print(f"\n--- Your {difficulty.capitalize()} Quiz ---")
    for i, q in enumerate(quiz, start=1):
        print(f"\nQ{i}. {q['question']}")
        for idx, option in enumerate(q["options"], start=1):
            print(f"   {idx}. {option}")

    print("\nGood luck!\n")


if __name__ == "__main__":
    run_quiz()
