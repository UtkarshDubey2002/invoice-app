import streamlit as st
from PIL import Image
import pytesseract
import openai
import os
import json
from dotenv import load_dotenv

import sys
print(sys.executable)
# Load API key from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# === GPT Field Extraction Function ===
def extract_invoice_fields(text):
    prompt = f"""
    Extract key invoice details from the following OCR text:
    \"\"\"
    {text}
    \"\"\"
    Provide the result in this JSON format:
    {{
        "Invoice Number": "...",
        "Invoice Date": "...",
        "Vendor Name": "...",
        "Total Amount": "...",
        "Tax Amount": "...",
        "Due Date": "...",
        "GSTIN": "...",
        "PAN": "..."
    }}
    """
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an invoice processing assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )
    return response.choices[0].message.content

# === GST Summary Generator ===
def generate_gst_summary(extracted_data):
    if isinstance(extracted_data, str):
        extracted_data = json.loads(extracted_data)

    gst_summary = {
        "GSTIN": extracted_data.get("GSTIN", "N/A"),
        "Taxable Amount": extracted_data.get("Total Amount", "N/A"),
        "Tax Breakdown": {
            "CGST": round(float(extracted_data.get("Tax Amount", 0)) / 2, 2),
            "SGST": round(float(extracted_data.get("Tax Amount", 0)) / 2, 2),
            "IGST": 0.00  # Placeholder
        }
    }
    return gst_summary

# === ITR Summary Generator ===
def generate_itr_summary(extracted_data):
    if isinstance(extracted_data, str):
        extracted_data = json.loads(extracted_data)

    itr_summary = {
        "PAN": extracted_data.get("PAN", "N/A"),
        "Total Income": extracted_data.get("Total Amount", "N/A"),
        "Deductions": "Standard (₹50,000)",  # Hardcoded
        "Estimated Tax Payable": extracted_data.get("Tax Amount", "N/A"),
        "Suggested ITR Form": "ITR-1 (Sahaj)"
    }
    return itr_summary

# === Streamlit UI ===
st.title("Invoice AI Processor with GST & ITR Summary")

uploaded_file = st.file_uploader("Upload an invoice (JPG, PNG only)", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Invoice", use_column_width=True)

    # === OCR ===
    extracted_text = pytesseract.image_to_string(image)
    st.subheader("OCR Extracted Text")
    st.text_area("Text", extracted_text, height=200)

    # === GPT Extraction ===
    if extracted_text:
        extracted_data = extract_invoice_fields(extracted_text)
        st.subheader("LLM Extracted Fields")
        st.json(json.loads(extracted_data))

        # === GST & ITR Summary ===
        st.subheader("📑 GST Summary")
        gst_data = generate_gst_summary(extracted_data)
        st.json(gst_data)

        st.subheader("🧾 ITR Summary")
        itr_data = generate_itr_summary(extracted_data)
        st.json(itr_data)
