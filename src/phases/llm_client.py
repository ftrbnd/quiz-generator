# -*- coding: utf-8 -*-
# src/phases/llm_client.py

import os
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is missing.")

DEFAULT_MODEL = "llama-3.3-70b-versatile"

def _get_client() -> Groq:
    # Debug: print first 8 chars to verify key is loaded
    print("DEBUG: Using Groq API key:", API_KEY[:8] + "...")
    return Groq(api_key=API_KEY)

def chat_completion(
    messages: List[dict],
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 512,
) -> str:
    client = _get_client()
    resp = client.chat.completions.create(
        model=model or DEFAULT_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )
    return resp.choices[0].message.content

def generate_quiz_from_text(
    source_text: str,
    num_questions: int = 5,
    question_types: Optional[List[str]] = None,
) -> str:
    if question_types is None:
        question_types = []
    type_str = ", ".join(question_types) if question_types else "any type"
    system_msg = (
        "You are an expert quiz generator. "
        "For the input below, create a quiz in Markdown consisting of questions and answers."
    )
    user_msg = f"""Create **{num_questions}** questions (with answers) based on the material below.
Use question types: {type_str}.
After each question, put an "Answer:" line with the correct answer.
Format using Markdown.

SOURCE:
\"\"\"{source_text}\"\"\"  
"""
    return chat_completion([
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ])

