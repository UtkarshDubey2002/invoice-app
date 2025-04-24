import streamlit as st
from PIL import Image
import requests
import openai
import io
import cv2
import numpy as np

# --- Function to extract text using OCR.Space API ---
def ocr_space_image(image, api_key):
    url_api = "https://api.ocr.space/parse/image"
    _, encoded_img = cv2.imencode('.jpg', image)
    response = requests.post(
        url_api,
        files={"filename.jpg": encoded_img.tobytes()},
        data={"apikey": api_key, "language": "eng"},
    )
    result = response.json()
    return result.get("ParsedResults")[0]["ParsedText"]

# --- Function to extract invoice fields using GPT ---
def extract_invoice_fields(text, openai_api_key):
    openai.api_key = openai_api_key
    prompt = f"""
    Extract the following invoice fields from the text below:
    - Invoice Number
    - Invoice Date
    - Vendor Name
    - Total Amount
    - Tax Amount (if any)

    Text:
    {text}

    Respond in JSON format with keys: invoice_number, invoice_date, vendor_name, total_amount, tax_amount.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response['choices'][0]['message']['content']

# --- Streamlit UI ---
st.title("🧾 Invoice Field Extractor")
st.markdown("Upload an invoice and extract key fields using OCR and GPT!")

ocr_api_key = st.text_input("🔑 Enter your OCR.Space API Key", type="password")
openai_api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

uploaded_file = st.file_uploader("📤 Upload Invoice Image or PDF", type=["jpg", "jpeg", "png"])

if uploaded_file and ocr_api_key and openai_api_key:
    image = Image.open(uploaded_file).convert("RGB")
    img_np = np.array(image)
    
    st.image(image, caption="📄 Uploaded Invoice", use_column_width=True)

    with st.spinner("🔍 Extracting text from image..."):
        extracted_text = ocr_space_image(img_np, ocr_api_key)

    st.subheader("📝 Extracted Text")
    st.text_area("OCR Output", extracted_text, height=200)

    with st.spinner("🤖 Analyzing with GPT..."):
        gpt_response = extract_invoice_fields(extracted_text, openai_api_key)

    st.subheader("📊 Invoice Fields")
    st.json(gpt_response)
