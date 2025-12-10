# ONE SIMPLE PYTHON FILE — User Story Implementation
#
# As an instructor, I want to tag questions by topic or
# standard so that I can analyze performance by curriculum area.
#
# Criteria:
# - Tags can be added to any question
# - Reports summarize scores by tag
# - Tags can be filtered during quiz creation

import json

# 1. Question bank with TAGS
question_bank = [
    {
        "question": "What does NLP stand for?",
        "options": ["Natural Language Processing", "New Logic Principle", "Node Link Protocol", "Neural Language Path"],
        "correct_index": 0,
        "tags": ["NLP", "Basics"]
    },
    {
        "question": "What is overfitting in ML?",
        "options": ["Model too fitted to training data", "Lack of data", "Too many layers", "None"],
        "correct_index": 0,
        "tags": ["Machine Learning", "Modeling"]
    },
    {
        "question": "What is a neural network?",
        "options": ["A model inspired by the human brain", "A networking cable", "A file system", "None"],
        "correct_index": 0,
        "tags": ["Deep Learning", "Neural Networks"]
    }
]

# 2. Filter questions by tag BEFORE quiz generation
def filter_by_tag(questions, selected_tags):
    filtered = []
    for q in questions:
        if any(tag in q["tags"] for tag in selected_tags):
            filtered.append(q)
    return filtered

# 3. Simulate student answers to calculate tag performance
def calculate_tag_scores(questions, student_answers):
    tag_scores = {}

    for q, ans in zip(questions, student_answers):
        is_correct = ans == q["correct_index"]

        for tag in q["tags"]:
            if tag not in tag_scores:
                tag_scores[tag] = {"correct": 0, "total": 0}

            tag_scores[tag]["total"] += 1
            if is_correct:
                tag_scores[tag]["correct"] += 1

    return tag_scores

# 4. Create a summary report by tag
def generate_tag_report(tag_scores):
    print("\n----- TAG PERFORMANCE REPORT -----\n")
    for tag, score in tag_scores.items():
        accuracy = (score["correct"] / score["total"]) * 100
        print(f"Tag: {tag}")
        print(f"  Correct: {score['correct']} / {score['total']}")
        print(f"  Accuracy: {accuracy:.2f}%\n")

def run_question_tags():
    print("Available Tags in Question Bank:")
    all_tags = sorted({tag for q in question_bank for tag in q["tags"]})
    print(all_tags)

    # Choose tags for this quiz
    print("\nSelect tags for your quiz (comma separated):")
    selected = input("Tags: ").split(",")

    # Clean input
    selected_tags = [t.strip() for t in selected if t.strip()]

    # Filter questions based on chosen tags
    quiz_questions = filter_by_tag(question_bank, selected_tags)

    print("\nQuiz Created with Questions Tagged:", selected_tags)
    for i, q in enumerate(quiz_questions, 1):
        print(f"{i}. {q['question']} (Tags: {q['tags']})")

    # Simulate student answers for demonstration
    # In a real system, this would come from user submissions
    print("\nEnter student answers (0,1,2,3) for each question:")
    student_answers = []
    for q in quiz_questions:
        ans = int(input(f"Answer for '{q['question']}': "))
        student_answers.append(ans)

    # Calculate tag performance
    tag_scores = calculate_tag_scores(quiz_questions, student_answers)

    # Show the tag-based report
    generate_tag_report(tag_scores)

    # Save template
    with open("tag_template.json", "w") as f:
        json.dump({"selected_tags": selected_tags}, f, indent=4)
    print("Tag template saved as tag_template.json")


# 5. RUN EVERYTHING IN ONE GO
if __name__ == "__main__":
    run_question_tags()