import os
import requests
from typing import Tuple

# --------------------------
# Hugging Face Setup
# --------------------------

HF_API_KEY = os.getenv("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")  # set this in Streamlit Cloud secrets
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")


def request_huggingface(prompt: str, max_tokens: int = 256) -> str:
    """Send a request to Hugging Face Inference API and return generated text."""
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()

    # HF returns list of dicts with 'generated_text'
    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]
    return str(result)


# --------------------------
# Core Interview Logic
# --------------------------

def generate_question(domain: str, difficulty: int) -> str:
    """Generate a new Excel interview question based on domain and difficulty."""
    prompt = (
        f"Generate one interview-style Excel question for the {domain} domain.\n"
        f"Difficulty level: {difficulty} (1=easy, 3=hard).\n"
        "Return only the question, without explanations or answers."
    )
    return request_huggingface(prompt, max_tokens=128)


def evaluate_answer(user_answer: str, correct_answer: str, question_text: str) -> Tuple[float, str]:
    """Evaluate user answer using Hugging Face model and return (score, feedback)."""
    prompt = f"""
    Question: {question_text}
    Correct Answer: {correct_answer}
    User Answer: {user_answer}

    Compare the user answer with the correct answer.
    - Give a score between 0 and 1 (0 = wrong, 1 = correct, 0.5 = partially correct).
    - Provide short, clear feedback explaining why.
    """

    response_text = request_huggingface(prompt, max_tokens=256)

    # crude score extraction
    score = 0.0
    text_lower = response_text.lower()
    if "1" in text_lower:
        score = 1.0
    elif "0.5" in text_lower:
        score = 0.5
    elif "0" in text_lower:
        score = 0.0

    return score, response_text.strip()
