from fpdf import FPDF
import streamlit as st
from io import BytesIO

# Generate PDF in memory
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="AI-Powered Excel Mock Interviewer Report", ln=True, align="C")
    pdf.ln(10)
    pdf.multi_cell(0, 10, "This is the generated report content...\nAdd interview summary, scores, feedback here.")
    
    # Save PDF to a bytes buffer instead of disk
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer

pdf_file = create_pdf()

# Streamlit download button
st.download_button(
    label="Download Report as PDF",
    data=pdf_file,
    file_name="mock_interview_report.pdf",
    mime="application/pdf"
)
