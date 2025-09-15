# frontend/app.py
import streamlit as st
from datetime import datetime
import interview_logic as interview_logic  # Your logic file
import pathlib

# Initialize session state
if 'session' not in st.session_state:
    st.session_state.session = {}

def clear_session_state():
    st.session_state.session = {}

def start_interview(name, email, domain):
    session_id = name + "_" + email + "_" + datetime.now().strftime("%Y%m%d%H%M%S")
    session = {
        "session_id": session_id,
        "name": name,
        "email": email,
        "domain": domain.lower(),
        "history": [],
        "difficulty": 5,
        "num_asked": 0,
        "num_correct": 0,
        "num_wrong": 0,
        "finished": False,
        "transcript_path": None
    }

    question, correct_answer = interview_logic.generate_question(
        session["domain"],
        session["difficulty"],
        session["num_asked"],
        session["num_correct"],
        session["num_wrong"]
    )
    session["current_question"] = question
    session["correct_answer"] = correct_answer
    session["num_asked"] = 1

    st.session_state.session = session
    return question, session["num_asked"]

def submit_answer(user_answer):
    session = st.session_state.session
    if session.get("finished"):
        return

    score, explanation = interview_logic.evaluate_answer(
        user_answer,
        session["correct_answer"],
        session["current_question"]
    )

    session["history"].append({
        "question": session["current_question"],
        "user_answer": user_answer,
        "correct_answer": session["correct_answer"],
        "score": float(score),
        "explanation": explanation
    })

    # Update counters and difficulty
    if float(score) > 0.7:
        session["num_correct"] += 1
        session["difficulty"] = min(10, session["difficulty"] + 1)
    elif float(score) < 0.4:
        session["num_wrong"] += 1
        session["difficulty"] = max(0, session["difficulty"] - 1)

    # Finish interview after 10 questions
    if session["num_asked"] >= 10:
        session["finished"] = True
        finished_time = datetime.now()
        filename = interview_logic.save_transcript(
            session["name"],
            session["email"],
            session["history"],
            session["domain"],
            session["num_asked"],
            session["num_correct"],
            session["num_wrong"],
            finished_time
        )
        session["transcript_path"] = filename
        return session

    # Generate next question
    session["num_asked"] += 1
    question, correct_answer = interview_logic.generate_question(
        session["domain"],
        session["difficulty"],
        session["num_asked"],
        session["num_correct"],
        session["num_wrong"]
    )
    session["current_question"] = question
    session["correct_answer"] = correct_answer
    return score, explanation, question, session["num_asked"]

def skip_question():
    return submit_answer("skip")

def exit_interview():
    session = st.session_state.session
    session["finished"] = True
    finished_time = datetime.now()
    filename = interview_logic.save_transcript(
        session["name"],
        session["email"],
        session["history"],
        session["domain"],
        session["num_asked"],
        session["num_correct"],
        session["num_wrong"],
        finished_time
    )
    session["transcript_path"] = filename
    return session

# ----------------- Streamlit UI -----------------
st.set_page_config(page_title="Excel Mock Interviewer", layout="centered")
st.title("Dynamic Excel Mock Interviewer")

if not st.session_state.session:
    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        domain = st.selectbox("Select Domain", ["Data Analysis", "Finance", "Operation"])
        start = st.form_submit_button("Start Interview")

        if start:
            if not name.strip() or not email.strip():
                st.error("Please enter your full name and a valid email address.")
            else:
                question, q_num = start_interview(name.strip(), email.strip(), domain)
                st.session_state.answer_input_key = 0
                st.rerun()
else:
    session = st.session_state.session
    if session.get("finished"):
        st.success("Interview finished!")
        st.markdown("### Final Results")
        st.markdown(f"- Questions Asked: {session['num_asked'] - 1}")
        st.markdown(f"- Correct Answers: {session['num_correct']}")
        st.markdown(f"- Wrong Answers: {session['num_wrong']}")
        final_score = (session['num_correct'] / session['num_asked']) * 100 if session['num_asked'] else 0
        st.markdown(f"- Final Score: {round(final_score,2)}% ✅")

        st.markdown("### Question-wise Performance")
        for i, entry in enumerate(session.get("history", []), 1):
            st.markdown(f"**Q{i}: {entry['question']}**")
            st.markdown(f"- Your Answer: {entry['user_answer']}")
            st.markdown(f"- Correct Answer: {entry['correct_answer']}")
            st.markdown(f"- Score: {entry['score']:.2f}")
            st.markdown(f"- Feedback: {entry['explanation']}")
            st.markdown("---")

        # Transcript download button
        transcript_path = session.get("transcript_path")
        if transcript_path and pathlib.Path(transcript_path).exists():
            with open(transcript_path, "rb") as f:
                st.download_button(
                    label="Download Transcript",
                    data=f,
                    file_name=pathlib.Path(transcript_path).name,
                    mime="text/plain"
                )

        if st.button("Next Candidate"):
            clear_session_state()
            st.rerun()

    else:
        st.markdown(f"### Question {session['num_asked']}:")
        st.write(session["current_question"])

        with st.form("answer_form"):
            key_value = st.session_state.get("answer_input_key", 0)
            answer = st.text_area("Your Answer", height=150, key=f"answer_input_{key_value}")
            col1, col2, col3 = st.columns(3)
            with col1:
                submit = st.form_submit_button("Submit Answer")
            with col2:
                skip = st.form_submit_button("Skip Question")
            with col3:
                exit_ = st.form_submit_button("Exit Interview")

        if submit and answer.strip():
            score, explanation, next_q, q_num = submit_answer(answer.strip())
            st.session_state.answer_input_key = key_value + 1
            st.session_state.score = score
            st.session_state.feedback = explanation
            st.session_state.session["current_question"] = next_q
            st.session_state.session["num_asked"] = q_num
            st.rerun()

        if skip:
            score, explanation, next_q, q_num = skip_question()
            st.session_state.answer_input_key = key_value + 1
            st.session_state.session["current_question"] = next_q
            st.session_state.session["num_asked"] = q_num
            st.rerun()

        if exit_:
            exit_interview()
            st.rerun()

        if st.session_state.get('score') is not None:
            st.markdown(f"### Last Answer Score: {st.session_state.score:.2f}")
            st.markdown(f"**Feedback:** {st.session_state.feedback}")

