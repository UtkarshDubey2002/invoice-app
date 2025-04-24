import streamlit as st
from PIL import Image
import pytesseract
import io

# Streamlit UI
st.title("Invoice Text Extraction")

# Upload an image
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg", "bmp"])

if uploaded_file is not None:
    # Open the image using PIL
    image = Image.open(uploaded_file)

    # Display the image
    st.image(image, caption="Uploaded Image.", use_column_width=True)

    # Extract text from image using pytesseract
    extracted_text = pytesseract.image_to_string(image)

    # Display extracted text
    st.subheader("Extracted Text:")
    st.write(extracted_text)
