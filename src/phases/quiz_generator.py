import os
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sklearn.feature_extraction.text import TfidfVectorizer


class QuizAI:
    def __init__(self):
        self.documents = []

        # Load model
        model_name = "google/flan-t5-base"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        # Text generation pipeline
        self.generator = pipeline(
            "text2text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=200
        )

    def upload_document(self, file_path):
        """Read and save uploaded text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.documents.append(content)
        return "Document uploaded successfully!"

    def detect_material(self):
        """Extract top 5 keyword topics using TF-IDF"""
        if not self.documents:
            return "No document uploaded."

        vectorizer = TfidfVectorizer(stop_words='english')
        X = vectorizer.fit_transform(self.documents)

        feature_names = vectorizer.get_feature_names_out()
        scores = X.toarray().sum(axis=0)

        top_indices = scores.argsort()[::-1][:5]
        keywords = [feature_names[i] for i in top_indices]

        return f"Detected material keywords: {', '.join(keywords)}"

    def generate_quiz(self):
        """Generate 5 multiple-choice questions"""
        if not self.documents:
            return ""

        content = self.documents[-1]

        prompt = f"""
Generate 5 multiple-choice quiz questions based on the following text.

Text:
{content}

Each question must have:
- A question
- Four options (a, b, c, d)
- Mark the correct answer with (*)

Format:

1. Question text
a) option
b) option
c) option
d) option
        """

        output = self.generator(prompt)[0]["generated_text"]
        return output

    
    def extract_first_question(self, quiz_text):
        """Extract only the first question block from the generated quiz"""
        lines = quiz_text.strip().split("\n")

        first_q = []
        collecting = False

        for line in lines:
            line_strip = line.strip()

            if line_strip.startswith("1.") or line_strip.lower().startswith("question"):
                collecting = True

            if collecting:
                first_q.append(line)

            if line_strip.lower().startswith("d)"):
                break

        return "\n".join(first_q)

    def generate_explanations(self, quiz_text):
        """Generate explanation for the correct answer of the first question"""
        question = self.extract_first_question(quiz_text)

        prompt = f"""
Explain the correct answer to the following multiple-choice question.
Only give the explanation.

Question:
{question}

Provide a short and clear explanation.
"""

        output = self.generator(prompt)[0]["generated_text"]
        return output
