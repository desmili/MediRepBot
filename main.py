from fastapi import FastAPI
 
app = FastAPI()
 
# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
 
# Example endpoint with path parameters
@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
 
# Example endpoint with query parameters
@app.get("/search/")
def search(query: str):
    return {"query": query}
 
# POST request with a request body
from pydantic import BaseModel
 
class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None
 
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    text = ""

    # Determine file type and extract text
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
