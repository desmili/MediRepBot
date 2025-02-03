#MediRepBot
#DiagnoBot
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from pdf2image import convert_from_bytes
import PyPDF2
import openai
import io

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change "*" to your frontend URL for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API Key (Replace with your key)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Medical terms for validation
MEDICAL_TERMS = {"hemoglobin", "MRI", "X-ray", "WBC", "RBC", "platelets", "glucose", "cholesterol"}

@app.get("/")
def home():
    return {"message": "API is working!"}

def extract_text_from_pdf(pdf_bytes):
    """Extract text from a PDF"""
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text.strip()

def extract_text_from_image(image_bytes):
    """Extract text from an image using OCR"""
    try:
        images = convert_from_bytes(image_bytes)
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        text = ""
    return text.strip()

def is_medical_report(text):
    """Check if extracted text contains medical terms"""
    return any(term.lower() in text.lower() for term in MEDICAL_TERMS)

def summarize_text(text):
    """Summarize the medical report using OpenAI"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a medical assistant that simplifies reports for patients."},
            {"role": "user", "content": f"Summarize this medical report in layman's terms:\n{text}"}
        ]
    )
    return response["choices"][0]["message"]["content"].strip()

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    text = ""

    # Extract text based on file type
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
