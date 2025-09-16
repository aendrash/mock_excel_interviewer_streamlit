# 🎯 Dynamic Excel Mock Interviewer

A **Streamlit web app** that conducts dynamic Excel interviews using Hugging Face large language models (LLMs).  
Prepare for Excel-based roles in Data Analysis, Finance, and Operations with adaptive difficulty questions, real-time scoring, and detailed feedback.

---

## 🚀 Features

- Domain-specific Excel question generation (Data Analysis, Finance, Operations)  
- Adaptive difficulty based on candidate performance  
- Automated answer evaluation with detailed feedback  
- Downloadable interview transcript for review  
- Easy-to-use web interface deployed on Streamlit

---

## 🌐 Demo & Deployment

- **GitHub Repository:** [mock_excel_interviewer_streamlit](https://github.com/aendrash/mock_excel_interviewer_streamlit/tree/main)  
- **Live Application:** [Open in Streamlit](https://mockexcelinterviewerapp-qg4mwiwr2tf69rapgh5g3z.streamlit.app/)

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher  
- [Streamlit](https://streamlit.io/)  
- [huggingface_hub](https://huggingface.co/docs/huggingface_hub/)

### Setup Steps

```bash
# Clone the repository
git clone https://github.com/aendrash/mock_excel_interviewer_streamlit.git
cd mock_excel_interviewer_streamlit

# Install dependencies
pip install -r requirements.txt
Environment Variables
Set your Hugging Face API key in the environment variable HF_API_KEY.

Locally: add it to your .env file or system environment variables.

On Streamlit Cloud: add it via Settings → Secrets.

▶️ Usage
Run the app locally:

bash
Copy code
streamlit run app.py
Provide your full name, email, and select a domain.

Answer the Excel interview questions interactively.

Get scored feedback immediately after each answer.

After completing the interview, download your interview transcript for review.

🗂️ Project Structure
File	Purpose
app.py	Streamlit frontend UI and session logic
interview_logic.py	Core interview question generation & evaluation logic
requirements.txt	Python dependencies

🤝 Contributing
Contributions, issues, and feature requests are welcome!
Check the issues page and follow standard GitHub flow for pull requests.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

📝 Acknowledgments
Powered by Hugging Face large language models

Built with Streamlit for an interactive web app experience

Thank you for checking out the Dynamic Excel Mock Interviewer!
