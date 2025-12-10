import json
import random

# QUESTION POOLS (example)
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

# Number of questions to pick from each pool
pool_settings = {
    "Topic 1: NLP": 1,
    "Topic 2: Machine Learning": 1,
    "Topic 3: Deep Learning": 1
}


# Generate quiz using question pools
def generate_quiz_from_pools(pools, settings):
    final_quiz = []
    
    for topic, questions in pools.items():
        amount = settings.get(topic, 0)

        # Randomly choose questions from each pool
        chosen = random.sample(questions, amount)

        # Add selected questions to final quiz
        final_quiz.extend(chosen)

    return final_quiz


# Save pool settings (quiz template)
def save_template(settings, filename="quiz_template.json"):
    with open(filename, "w") as f:
        json.dump(settings, f, indent=4)
    print(f"Template saved as {filename}")


# RUN EVERYTHING (one go)
if __name__ == "__main__":
    print("Generating quiz from question pools...\n")

    quiz = generate_quiz_from_pools(question_pools, pool_settings)

    print("Final Quiz Questions:")
    for i, q in enumerate(quiz, start=1):
        print(f"{i}. {q}")

    # Save the pool settings
    save_template(pool_settings)
