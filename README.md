# COMP 582 - Quiz Generation Project by Group P

## Prerequisites

- Python 3.12
- Groq API Key-- open Groq account and use this when running:
  import os  
  os.environ["GROQ_API_KEY"] = "your_secret_key_here"

Or add an .env file with API key

## Installation

1. Clone the repo
   ```sh
   git clone https://github.com/ftrbnd/quiz-generator.git
   ```
2. Install required packages
   ```sh
   make install
   ```
3. Activate the virtual environment
   ```sh
   make activate
   ```
4. Run gradio inside the virtual environment
   ```sh
   gradio src/app.py
   ```
