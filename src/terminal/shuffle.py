import random


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
]


def shuffle_answers(question):
    """
    Takes a question dictionary and returns a new version
    where the answer choices are shuffled but the correct
    answer remains accurately mapped.
    """
    # Copy question to avoid mutating original
    q = question.copy()
    
    # Copy options and shuffle them
    shuffled_options = q["options"][:]
    random.shuffle(shuffled_options)
    
    # Find the new index where correct answer moved
    correct_answer = q["answer"]
    new_correct_answer = correct_answer  # same value, new position in list
    
    q["options"] = shuffled_options
    q["answer"] = new_correct_answer
    
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

    # Shuffle answer options PER QUESTION (this user story!)
    return [shuffle_answers(q) for q in selected]


def run_quiz():
    print("Choose difficulty: easy / medium / hard")

    while True:
        diff = input("Enter difficulty: ").strip().lower()
        try:
            quiz = generate_quiz(diff)
            break
        except ValueError as e:
            print(e)

    print(f"\n--- Your {diff.capitalize()} Quiz ---")

    for i, q in enumerate(quiz, start=1):
        print(f"\nQ{i}. {q['question']}")
        for idx, option in enumerate(q["options"], start=1):
            print(f"   {idx}. {option}")

    print("\nGood luck!")
    

if __name__ == "__main__":
    run_quiz()
