from typing import Union
from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz  
#import io
import pdfplumber
from io import BytesIO

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
  
@app.post("/pdf-to-text-pdf/")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    try:
        # Read PDF file
        pdf_bytes = await file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Extract text from all pages
        text = "\n".join(page.get_text() for page in pdf_document)

        return {"filename": file.filename, "extracted_text": text}

    except Exception as e:
        return {"error": str(e)}
      
      
@app.post("/pdf-to-text-pdfplumber")
async def extract_text_from_pdf(file: UploadFile = File(...)):
    # Check if the uploaded file is a PDF
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read the uploaded file into memory
        contents = await file.read()
        
        # Use BytesIO to convert bytes to a file-like object
        with BytesIO(contents) as pdf_file:
            with pdfplumber.open(pdf_file) as pdf:
                extracted_text = ""
                # Extract text from each page
                for page in pdf.pages:
                    extracted_text += page.extract_text() + "\n\n"
                
                return {"text": extracted_text.strip()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")