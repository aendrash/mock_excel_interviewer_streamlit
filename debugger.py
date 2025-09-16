# app.py
import streamlit as st
import os
from huggingface_hub import InferenceClient

st.set_page_config(page_title="HF API Test", layout="centered")
st.title("🚀 Hugging Face API Test")

# 1. Check if API key exists
hf_api_key = os.getenv("HF_API_KEY")
if not hf_api_key:
    st.error("❌ No HF_API_KEY found! Please add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

try:
    # 2. Init client
    client = InferenceClient(api_key=hf_api_key, provider="cerebras")

    # 3. Make a simple request
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": "Say Hello"}],
        max_tokens=10,
    )

    response_text = completion.choices[0].message.content
    st.success("✅ API call successful!")
    st.write("Response:", response_text)

except Exception as e:
    st.error("⚠️ API call failed!")
    st.code(str(e))
