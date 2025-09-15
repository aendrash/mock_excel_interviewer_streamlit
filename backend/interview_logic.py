import requests
import json
import os
from datetime import datetime
from time import sleep

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral:7b")
MAX_LLM_RETRIES = int(os.getenv("MAX_LLM_RETRIES", "2"))


def create_llm_prompt(domain, difficulty, num_asked, num_correct, num_wrong):
    return (
        f"You are a knowledgeable Excel interviewer specialized in {domain} domain.\n"
        f"The candidate has answered {num_asked} interview questions with {num_correct} correct and {num_wrong} wrong answers so far.\n"
        f"Ask the next question at difficulty level {difficulty} (0=easy, 10=hard).\n"
        "Provide a clear, practical Excel interview question for this domain and difficulty level, and also supply an ideal correct answer as reference.\n"
        "Format your response as:\n"
        "Question: <your question text>\n"
        "Answer: <the correct answer as concise formula/text>\n"
        "Do not include anything else or explanation."
    )


def request_llm(prompt, model=None, max_tokens=400):
    """
    Request the local Ollama-like API (configurable via OLLAMA_URL).
    Returns the full text response (string). Includes simple retry logic.
    """
    url = OLLAMA_URL
    used_model = model or OLLAMA_MODEL
    payload = {
        "model": used_model,
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": max_tokens,
        "stream": True,
    }

    attempt = 0
    while attempt <= MAX_LLM_RETRIES:
        try:
            response = requests.post(url, json=payload, stream=True, timeout=30)
            response.raise_for_status()
            full_response = ""
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        full_response += chunk.get("response", "")
                        if chunk.get("done", False):
                            break
                    except Exception:
                        # If not JSON-chunked, append raw decoded text
                        try:
                            full_response += line.decode("utf-8")
                        except Exception:
                            pass
            return full_response.strip()
        except Exception as e:
            attempt += 1
            if attempt > MAX_LLM_RETRIES:
                raise
            sleep(1)


def parse_question_answer(text):
    lines = text.split("\n")
    question = ""
    answer = ""
    reading_question = False
    reading_answer = False
    for line in lines:
        line = line.strip()
        if line.lower().startswith("question:"):
            question = line[len("question:"):].strip()
            reading_question = True
            reading_answer = False
        elif line.lower().startswith("answer:"):
            answer = line[len("answer:"):].strip()
            reading_question = False
            reading_answer = True
        else:
            if reading_question:
                question += " " + line
            elif reading_answer:
                answer += " " + line
    return question.strip(), answer.strip()


def create_scoring_prompt(user_answer, correct_answer, question_text):
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


def llm_score_answer(user_answer, correct_answer, question_text):
    prompt = create_scoring_prompt(user_answer, correct_answer, question_text)
    response_text = request_llm(prompt, max_tokens=256)
    score = 0.0
    explanation = ""
    for line in response_text.split("\n"):
        line = line.strip()
        if line.lower().startswith("score:"):
            try:
                score_str = line.split(":", 1)[1].strip()
                score = float(score_str)
                score = max(0.0, min(score, 1.0))
            except Exception:
                score = 0.0
        elif line.lower().startswith("explanation:"):
            explanation = line.split(":", 1)[1].strip()
    return score, explanation


def save_transcript(candidate_name, email, history, domain, num_asked, num_correct, num_wrong, finished_time):
    safe_name = candidate_name.replace(" ", "_")
    safe_email = email.replace("@", "_at_").replace(".", "_")
    timestr = finished_time.strftime('%Y%m%d_%H%M%S')

    if not os.path.exists("report"):
        os.makedirs("report")

    filename = os.path.join("report", f'{safe_name}_{safe_email}_{timestr}.txt')

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Excel Mock Interview Report\n")
        f.write(f"Name    : {candidate_name}\n")
        f.write(f"Email   : {email}\n")
        f.write(f"Domain  : {domain}\n")
        f.write(f"Date    : {finished_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Number of Questions: {num_asked - 1}\n")
        f.write(f"Correct Answers   : {num_correct}\n")
        f.write(f"Wrong Answers     : {num_wrong}\n\n")
        for i, entry in enumerate(history, 1):
            f.write(f"--- Q{i} ---\n")
            f.write(f"Question:\n{entry.get('question', '')}\n")
            f.write(f"Your answer:\n{entry.get('user_answer', '')}\n")
            f.write(f"Correct answer:\n{entry.get('correct_answer', '')}\n")
            f.write(f"Score: {entry.get('score', 0.0):.2f}\n")
            f.write(f"Explanation: {entry.get('explanation', '')}\n\n")
    print(f"\nTranscript saved as: {filename}")


# Helper methods to match FastAPI usage

def generate_question(domain, difficulty=5, num_asked=0, num_correct=0, num_wrong=0):
    prompt = create_llm_prompt(domain, difficulty, num_asked, num_correct, num_wrong)
    # Retry loop to get a decent response
    for attempt in range(MAX_LLM_RETRIES + 1):
        try:
            response_text = request_llm(prompt)
            question, correct_answer = parse_question_answer(response_text)
            if question and correct_answer:
                return question, correct_answer
        except Exception:
            pass
        sleep(1)
    # Fallback default question
    fallback_q = "Create a sample Excel question: How to sum values in column B where column A equals 'X'?"
    fallback_a = "Use SUMIF: =SUMIF(A:A, \"X\", B:B)"
    return fallback_q, fallback_a

def evaluate_answer(user_answer, correct_answer, question_text):
    if isinstance(user_answer, str) and user_answer.lower().strip() == 'skip':
        return 0.0, "Question skipped by user."
    return llm_score_answer(user_answer, correct_answer, question_text)
