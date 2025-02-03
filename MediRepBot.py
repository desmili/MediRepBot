#DiagnoBot
from fastapi import FastAPI, File, UploadFile
import pytesseract
from pdf2image import convert_from_bytes
import PyPDF2
import openai
import io

app = FastAPI()

# OpenAI API Key (Replace with your own API key)
openai.api_key = "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"

# Sample list of medical terms for validation
MEDICAL_TERMS = {"hemoglobin", "MRI", "X-ray", "WBC", "RBC", "platelets", "glucose", "cholesterol"}

def extract_text_from_pdf(pdf_bytes):
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()

def extract_text_from_image(image_bytes):
    try:
        images = convert_from_bytes(image_bytes)
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        text = ""
    return text.strip()

def is_medical_report(text):
    return any(term.lower() in text.lower() for term in MEDICAL_TERMS)

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a medical assistant that summarizes medical reports in simple terms."},
            {"role": "user", "content": f"Summarize this medical report in layman's terms:\n{text}"}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    text = ""
    
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(contents)
    elif file.filename.endswith(('.png', '.jpg', '.jpeg')):
        text = extract_text_from_image(contents)
    else:
        return {"error": "Unsupported file format. Please upload a PDF or image file."}
    
    if not text:
        return {"error": "Could not extract text from the file."}
    
    if not is_medical_report(text):
        return {"error": "This does not appear to be a medical report."}
    
    summary = summarize_text(text)
    
    return {"summary": summary}