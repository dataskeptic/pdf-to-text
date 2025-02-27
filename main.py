from typing import Union
from fastapi import FastAPI, File, UploadFile, HTTPException
import fitz  
#import io
import pdfplumber
from io import BytesIO
from pdfminer.high_level import extract_text


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
  
@app.post("/pdf-to-text-fitz")   #PyMuPDF
async def extract_text_using_fitz(file: UploadFile = File(...)):
    try:
        # Read PDF file
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        pdf_bytes = await file.read()
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

        # Extract text from all pages
        text = "\n".join(page.get_text() for page in pdf_document)

        return {"file_name": file.filename, "extracted_text": text}

    except Exception as e:
        return {"error": str(e)}
      
      
@app.post("/pdf-to-text-pdfplumber")
async def extract_text_using_pdfplumber(file: UploadFile = File(...)):
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
                
                return {"file_name": file.filename, "extracted_text": extracted_text.strip()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    
    
@app.post("/pdf-to-text-pdfminer")
async def extract_text_from_pdfminer(file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Read uploaded PDF into memory
        contents = await file.read()
        
        # Use BytesIO to create a file-like object
        with BytesIO(contents) as pdf_file:
            # Extract all text from PDF
            extracted_text = extract_text(pdf_file)
            return {"file_name": file.filename, "extracted_text": extracted_text.strip()}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")