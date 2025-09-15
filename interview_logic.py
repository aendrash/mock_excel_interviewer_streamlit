import os
import random
from typing import Tuple, List, Dict
from huggingface_hub import InferenceClient

# Init Hugging Face client
HF_API_KEY = os.getenv("HF_API_KEY")  # add this in Streamlit Cloud secrets
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
client = InferenceClient(model=MODEL_ID, token=HF_API_KEY)

# ---------------- Question Bank ----------------
QUESTION_BANK = [
    ("How to find the average of column C in Excel?", "Use AVERAGE: =AVERAGE(C:C)"),
    ("How to sum values in column B where column A equals 'X'?", "Use SUMIF: =SUMIF(A:A, \"X\", B:B)"),
    ("How to count cells in column D greater than 100?", "Use COUNTIF: =COUNTIF(D:D, \">100\")"),
    ("How to find duplicate values in column E?", "Use conditional formatting or =COUNTIF(E:E,E1)>1"),
    ("How to combine first and last names in Excel?", "Use CONCATENATE: =A1 & \" \" & B1"),
]

def generate_question(domain: str, difficulty: int, num_asked: int, num_correct: int, num_wrong: int) -> Tuple[str, str]:
    question, correct_answer = random.choice(QUESTION_BANK)
    return question, correct_answer

# ---------------- Hugging Face LLM ----------------
def request_llm(prompt: str, max_tokens: int = 256) -> str:
    response = client.text_generation(prompt, max_new_tokens=max_tokens, do_sample=True)
    return response

def llm_score_answer(user_answer: str, correct_answer: str, question_text: str) -> Tuple[float, str]:
    prompt = f"""
You are an Excel interview evaluator.
Question: {question_text}
Correct Answer: {correct_answer}
Candidate Answer: {user_answer}

Evaluate the candidate’s answer.
1. Give a score between 0.0 and 1.0 (float).
2. Explain why the score was given.
Format your reply as:
Score: <score>
Explanation: <explanation>
"""
    response_text = request_llm(prompt)

    # Parse
    score, explanation = 0.0, "Could not parse model response."
    for line in response_text.splitlines():
        if line.strip().lower().startswith("score:"):
            try:
                score = float(line.split(":", 1)[1].strip())
            except:
                score = 0.0
        if line.strip().lower().startswith("explanation:"):
            explanation = line.split(":", 1)[1].strip()
    return score, explanation

def evaluate_answer(user_answer: str, correct_answer: str, question_text: str) -> Tuple[float, str]:
    return llm_score_answer(user_answer, correct_answer, question_text)

def save_transcript(name: str, email: str, history: List[Dict], domain: str, num_asked: int, num_correct: int, num_wrong: int, finished_time) -> str:
    filename = f"{name}_{email}_{finished_time.strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w") as f:
        f.write(f"Candidate: {name} ({email})\n")
        f.write(f"Domain: {domain}\n")
        f.write(f"Finished: {finished_time}\n")
        f.write(f"Total Questions: {num_asked}, Correct: {num_correct}, Wrong: {num_wrong}\n\n")
        for i, entry in enumerate(history, 1):
            f.write(f"Q{i}: {entry['question']}\n")
            f.write(f"Answer: {entry['user_answer']}\n")
            f.write(f"Correct Answer: {entry['correct_answer']}\n")
            f.write(f"Score: {entry['score']:.2f}\n")
            f.write(f"Feedback: {entry['explanation']}\n\n")
    return filename
