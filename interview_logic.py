import os
from datetime import datetime
from time import sleep
from typing import Tuple, List, Dict
from huggingface_hub import InferenceClient

# Init Hugging Face client
HF_API_KEY = os.getenv("HF_API_KEY") or st.secrets.get("HF_API_KEY")
# add this in Streamlit Cloud secrets
# MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
client = InferenceClient(
    provider="cerebras",
    api_key=HF_API_KEY,
)
MAX_LLM_RETRIES = 2

# ---------------- LLM Prompts ----------------
def create_llm_question_prompt(domain: str, difficulty: int, num_asked: int, num_correct: int, num_wrong: int) -> str:
    return (
        f"You are an Excel interviewer specialized in {domain}.\n"
        f"Candidate so far: {num_asked} questions, {num_correct} correct, {num_wrong} wrong.\n"
        f"Next question difficulty: {difficulty} (0=easy, 10=hard).\n\n"
        "⚠️ IMPORTANT: Output ONLY in this exact format (no extra words):\n"
        "Question: <your question>\n"
        "Answer: <the correct Excel answer>\n"
    )


def create_llm_scoring_prompt(user_answer: str, correct_answer: str, question_text: str) -> str:
    return (
        "You are an expert Excel interviewer evaluator.\n"
        "Given the interview question:\n"
        f"\"{question_text}\"\n\n"
        "Correct answer:\n"
        f"{correct_answer}\n\n"
        "Candidate answer:\n"
        f"{user_answer}\n\n"
        "Evaluate the candidate's answer considering the following:\n"
        "- Accept formula answers even if rows/columns differ by one or minor variations in syntax, as long as logic is correct.\n"
        "- For questions about PivotTables or UI operations, award full credit if candidate describes correct creation steps or approach.\n"
        "- For multi-sheet summaries, accept Power Query, formulas, Consolidate tool, or VBA-based solutions.\n"
        "- For conceptual or complex problem questions, accept partial credit for reasonable approaches or stating the need for Solver/macros.\n"
        "- Award partial credit when the answer is mostly correct but misses some edge cases or details.\n"
        "- Do not penalize minor formatting or phrasing differences.\n"
        "Provide a clear numeric score between 0 (completely incorrect) and 1 (perfectly correct) on the first line.\n"
        "On the second line, provide a concise explanation summarizing the evaluation.\n"
        "Format strictly as:\n"
        "Score: <decimal number between 0 and 1>\n"
        "Explanation: <brief reasoning>"
    )

# ---------------- LLM Requests ----------------
# def request_llm(prompt: str, max_tokens: int = 400) -> str:
#     attempt = 0
#     while attempt <= MAX_LLM_RETRIES:
#         try:
#             completion = client.chat.completions.create(
#                 model="openai/gpt-oss-120b",
#                 messages=[{"role": "user", "content": prompt}],
#                 max_tokens=max_tokens,
#                 temperature=0.7,
#             )
#             # Extract text safely (works both locally & Streamlit Cloud)
#             try:
#                 print(completion.choices[0].message)
#             except:
#                 pass
#             return getattr(completion.choices[0].message, "content", None) or completion.choices[0].message.get("content", "")
#         except Exception as e:
#             attempt += 1
#             if attempt > MAX_LLM_RETRIES:
#                 raise e
#             sleep(1)


def request_llm(prompt: str, max_tokens: int = 400) -> str:
    """Send a prompt to the LLM and return its response text safely."""
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
        )
        response_text = completion.choices[0].message.content
        print("DEBUG LLM Response:", response_text)  # goes to Streamlit Cloud logs
        return response_text
    except Exception as e:
        print("❌ ERROR in request_llm")
        print("Prompt that failed:", prompt)
        print(traceback.format_exc())
        raise e  # propagate to app.py



# ---------------- Generate Question ----------------
# def parse_question_answer(text: str) -> Tuple[str, str]:
#     question, answer = "", ""
#     for line in text.splitlines():
#         clean = line.strip().lower()
#         if clean.startswith("question"):
#             question = line.split(":", 1)[1].strip()
#         elif clean.startswith("answer"):
#             answer = line.split(":", 1)[1].strip()

#     # Fallback: sometimes LLM returns in markdown ``` blocks
#     if not question or not answer:
#         import re
#         q_match = re.search(r"question\s*[:\-]\s*(.*)", text, re.I)
#         a_match = re.search(r"answer\s*[:\-]\s*(.*)", text, re.I)
#         if q_match:
#             question = q_match.group(1).strip()
#         if a_match:
#             answer = a_match.group(1).strip()

#     return question, answer


def parse_question_answer(text: str) -> Tuple[str, str]:
    """Parse Question and Answer from the model response."""
    question, answer = "", ""
    try:
        for line in text.split("\n"):
            clean = line.strip().lower()
            if clean.startswith("question"):
                question = line.split(":", 1)[1].strip() if ":" in line else line.split("-", 1)[1].strip()
            elif clean.startswith("answer"):
                answer = line.split(":", 1)[1].strip() if ":" in line else line.split("-", 1)[1].strip()
        print("DEBUG Parsed Question:", question)
        print("DEBUG Parsed Answer:", answer)
        return question, answer
    except Exception as e:
        print("❌ ERROR in parse_question_answer")
        print("Raw text:", text)
        print(traceback.format_exc())
        raise e

def generate_question(domain: str, difficulty: int, num_asked: int, num_correct: int, num_wrong: int) -> Tuple[str, str]:
    print(HF_API_KEY)
    prompt = create_llm_question_prompt(domain, difficulty, num_asked, num_correct, num_wrong)
    for attempt in range(MAX_LLM_RETRIES + 1):
        try:
            response_text = request_llm(prompt)
            question, correct_answer = parse_question_answer(response_text)
            print(" question " , question , " answer " ,answer)
            if question and correct_answer:
                return question, correct_answer
        except Exception:
            print(Exception)
            sleep(1)
    # fallback
    fallback_q = "Create a sample Excel question: How to sum values in column B where column A equals 'X'?"
    fallback_a = "Use SUMIF: =SUMIF(A:A, \"X\", B:B)"
    return fallback_q, fallback_a

# ---------------- Evaluate Answer ----------------
def evaluate_answer(user_answer: str, correct_answer: str, question_text: str) -> Tuple[float, str]:
    if user_answer.strip().lower() == "skip":
        return 0.0, "Question skipped by user."
    prompt = create_llm_scoring_prompt(user_answer, correct_answer, question_text)
    response_text = request_llm(prompt, max_tokens=256)
    score = 0.0
    explanation = "Could not parse response."
    for line in response_text.splitlines():
        if line.lower().startswith("score:"):
            try:
                score = float(line.split(":", 1)[1].strip())
                score = max(0.0, min(1.0, score))
            except:
                score = 0.0
        if line.lower().startswith("explanation:"):
            explanation = line.split(":", 1)[1].strip()
    return score, explanation

# ---------------- Save Transcript ----------------
def save_transcript(name: str, email: str, history: List[Dict], domain: str, num_asked: int, num_correct: int, num_wrong: int, finished_time) -> str:
    safe_name = name.replace(" ", "_")
    safe_email = email.replace("@", "_at_").replace(".", "_")
    timestr = finished_time.strftime('%Y%m%d_%H%M%S')
    filename = f"{safe_name}_{safe_email}_{timestr}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"Excel Mock Interview Report\n")
        f.write(f"Name    : {name}\n")
        f.write(f"Email   : {email}\n")
        f.write(f"Domain  : {domain}\n")
        f.write(f"Date    : {finished_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Questions: {num_asked}\n")
        f.write(f"Correct Answers: {num_correct}\n")
        f.write(f"Wrong Answers  : {num_wrong}\n\n")
        for i, entry in enumerate(history, 1):
            f.write(f"--- Q{i} ---\n")
            f.write(f"Question:\n{entry.get('question')}\n")
            f.write(f"Your answer:\n{entry.get('user_answer')}\n")
            f.write(f"Correct answer:\n{entry.get('correct_answer')}\n")
            f.write(f"Score: {entry.get('score', 0.0):.2f}\n")
            f.write(f"Explanation:\n{entry.get('explanation')}\n\n")
    return filename







