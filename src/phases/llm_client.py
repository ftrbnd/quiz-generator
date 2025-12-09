# -*- coding: utf-8 -*-
# src/phases/llm_client.py

import json
import os
from typing import List, Literal, Optional, TypedDict
from groq import Groq
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is missing.")

DEFAULT_MODEL = "llama-3.3-70b-versatile"

# Prevent model context-length failure
MAX_SOURCE_CHARS = 8000  # safe limit for most Groq models

QuestionType = Literal["fill_blank", "mcq", "t/f", "short_answer"]
class Question(TypedDict):
    question: str
    answer: str
    type: QuestionType

def _get_client() -> Groq:
    """Initialize Groq client with partial-key debug logging."""
    print("DEBUG: Using Groq API key prefix:", API_KEY[:8] + "...")
    return Groq(api_key=API_KEY)


def chat_completion(
    messages: List[dict],
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 512,
) -> str:
    """
    Wrapper for Groq chat completion requests.
    Provides a consistent interface and prevents massive token usage.
    """
    client = _get_client()

    response = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
        response_format={"type": "json_object"}
    )

    return response.choices[0].message.content

def _parse_questions(raw_response: str) -> List[Question]:
    """
    Parse and validate the JSON response from the LLM.
    Returns a typed list of Question objects.
    """
    try:
        data = json.loads(raw_response)
        
        # Handle different possible JSON structures
        if isinstance(data, list):
            questions = data
        elif isinstance(data, dict) and "questions" in data:
            questions = data["questions"]
        else:
            raise ValueError(f"Unexpected JSON structure: {data}")
        # TODO: multiple choice questions are not formatted properly
        # Validate and type-check each question
        validated_questions: List[Question] = []
        for q in questions:
            if not isinstance(q, dict):
                continue
                
            # Ensure required fields exist
            if "question" not in q or "answer" not in q or "type" not in q:
                print(f"WARNING: Skipping malformed question: {q}")
                continue
            
            # Validate type field
            if q["type"] not in ["fill_blank", "mcq", "t/f", "short_answer"]:
                print(f"WARNING: Invalid question type '{q['type']}', defaulting to 'short_answer'")
                q["type"] = "short_answer"
            
            validated_questions.append(Question(
                question=str(q["question"]),
                answer=str(q["answer"]),
                type=q["type"]
            ))
        
        return validated_questions
        
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        print(f"Raw response: {raw_response[:500]}...")
        return []
    except Exception as e:
        print(f"ERROR: Unexpected error parsing questions: {e}")
        return []


def generate_from_llm(
    source_text: str,
    num_questions: int = 5,
    question_types: Optional[List[str]] = None,
) -> str:
    """
    Generates a quiz using Groq LLM with context-size protection.
    Ensures oversized source text does NOT break the API.
    """
    if question_types is None:
        question_types = []

    # Convert the list into a readable string for the prompt.
    type_str = ", ".join(question_types) if question_types else "any type"

    # Prevent context-size overflow errors
    if len(source_text) > MAX_SOURCE_CHARS:
        print(f"DEBUG: Input text length {len(source_text)} exceeds limit; truncating.")
        source_text = source_text[:MAX_SOURCE_CHARS] + "\n\n[TRUNCATED]"

    system_msg = (
        "You are an expert quiz generator. "
        "Produce a structured Markdown quiz with questions followed by answers."
    )

    user_msg = f"""
Create **{num_questions}** quiz questions based on the material below.
Use question types: {type_str}.

Respond with a JSON object containing a "questions" array. Each question object must have:
- "question": the question text (string)
- "answer": the correct answer (string)
- "type": one of "fill_blank", "mcq", "t/f", or "short_answer"

For multiple choice questions (mcq), format the answer as: "A) option1, B) option2, C) option3, D) option4. Correct: A"

Example format:
{{
  "questions": [
    {{
      "question": "What is 2+2?",
      "answer": "4",
      "type": "short_answer"
    }}
  ]
}}

SOURCE MATERIAL:
\"\"\"{source_text}\"\"\"
"""

    raw_response = chat_completion(
        [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
    )
    return _parse_questions(raw_response)

