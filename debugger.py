import streamlit as st
import os
from huggingface_hub import InferenceClient

st.set_page_config(page_title="HF API Test", layout="centered")
st.title("🚀 Hugging Face API Test")

hf_api_key = os.getenv("HF_API_KEY")
if not hf_api_key:
    st.error("❌ No HF_API_KEY found! Please add it in Streamlit Cloud → Settings → Secrets.")
    st.stop()

st.write(f"🔑 HF_API_KEY loaded with length: {len(hf_api_key)}")

try:
    client = InferenceClient(api_key=hf_api_key)

    # Use a model that supports chat
    completion = client.chat.completions.create(
        model="mistralai/Mistral-7B-Instruct-v0.2",
        messages=[{"role": "user", "content": "Say Hello in one word"}],
        max_tokens=20,
    )

    # Some models return under `.choices[0].message.content`
    response_text = (
        completion.choices[0].message.content
        if completion.choices[0].message
        else completion.choices[0].delta.get("content", None)
    )

    if response_text:
        st.success("✅ API call successful!")
        st.write("Response:", response_text)
    else:
        st.warning("⚠️ API call succeeded but no text returned.")
        st.json(completion.model_dump())

except Exception as e:
    st.error("⚠️ API call failed!")
    st.code(str(e))
