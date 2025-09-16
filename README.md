
# 🎯 Excel Mock Interviewer

A Streamlit web app that conducts dynamic Excel interviews using Hugging Face large language models (LLMs). Prepare for Excel-based roles in Data Analysis, Finance, and Operations with adaptive difficulty questions, real-time scoring, and detailed feedback.

---

## 🚀 Features

- Domain-specific Excel question generation (Data Analysis, Finance, Operations)
- Adaptive difficulty based on candidate performance
- Automated answer evaluation with detailed feedback
- Downloadable interview transcript for review
- Easy-to-use web interface deployed on Streamlit

---

## 🌐 Demo & Deployment

- GitHub Repository: https://github.com/aendrash/mock_excel_interviewer_streamlit/tree/main
- Live Application: https://mockexcelinterviewerapp-qg4mwiwr2tf69rapgh5g3z.streamlit.app/

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- Streamlit
- huggingface_hub

### Setup Steps

Clone the repository
git clone https://github.com/aendrash/mock_excel_interviewer_streamlit.git
cd mock_excel_interviewer_streamlit

(Optional) Create and activate a virtual environment
python -m venv .venv

Windows
.venv\Scripts\activate

macOS/Linux
source .venv/bin/activate

Install dependencies
pip install -r requirements.txt

### Environment Variables

Set the Hugging Face API key in the environment variable HF_API_KEY.

- Local: add it to a .env file or system environment variables.
- Streamlit Cloud: add it via Settings → Secrets.

Example .env:
HF_API_KEY=hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXX

If using Streamlit Secrets (secrets.toml):
HF_API_KEY = "hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"

---

## ▶️ Usage

Run the app locally:

streamlit run app.py

Then:

- Enter full name and email, and select a domain.
- Answer Excel interview questions interactively.
- Receive scored feedback after each answer.
- Download the interview transcript upon completion.

---

## 🗂️ Project Structure

| File               | Purpose                                           |
|-------------------|---------------------------------------------------|
| app.py            | Streamlit frontend UI and session logic           |
| interview_logic.py| Core question generation and evaluation logic     |
| requirements.txt  | Python dependencies                               |
| README.md         | Project documentation                             |
| LICENSE           | Project license (MIT)                             |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome. Please open an issue to discuss proposed changes and follow standard GitHub flow for pull requests.

---

## 📄 License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## 📝 Acknowledgments

- Powered by Hugging Face large language models
- Built with Streamlit for an interactive web app experience
- Thanks for checking out the Dynamic Excel Mock Interviewer!
