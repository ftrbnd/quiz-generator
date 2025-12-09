# -*- coding: utf-8 -*-
# src/phases/llm_client.py

import os
from typing import List, Optional
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
    )

    return response.choices[0].message.content


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
Include an "Answer:" line directly under each question.
Respond ONLY in Markdown, well formatted.

SOURCE MATERIAL:
\"\"\"{source_text}\"\"\"
"""

    return chat_completion(
        [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ]
    )
