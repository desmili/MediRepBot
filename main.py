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


#MilindKey
#client = openai.OpenAI(api_key="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")
#MMDKey
#client = openai.OpenAI(api_key="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")
#DiagnoBotKey
client = openai.OpenAI(api_key="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", project="proj_SCqF62rYmcBujgn3QbEcZ2lI")
#openai.api_key = "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"



#print(response.choices[0].message.content)
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
    #gpt-3.5-turbo, gpt-4, gpt-4-turbo, gpt-4o-mini, GPT-4o
    response = client.chat.completions.create(
        model="gpt-4", 
            messages=[
            {"role": "system", "content": "You are a medical assistant that simplifies reports for patients."},
            {"role": "user", "content": f"Summarize this medical report in layman's terms:\n{text}"}
        ]
    )
    #return response["choices"][0]["message"]["content"].strip()
    return response.choices[0].message.content

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
