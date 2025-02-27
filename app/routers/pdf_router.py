from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services import pdf_service

router = APIRouter()

@router.post("/pdf-to-text-fitz", tags=["PDF Extraction"])
async def extract_text_using_fitz(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    pdf_bytes = await file.read()
    try:
        text = pdf_service.extract_text_fitz(pdf_bytes)
        return {"file_name": file.filename, "extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      

@router.post("/pdf-to-text-pdfplumber", tags=["PDF Extraction"])
async def extract_text_using_pdfplumber(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    contents = await file.read()
    try:
        text = pdf_service.extract_text_pdfplumber(contents)
        return {"file_name": file.filename, "extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
      

@router.post("/pdf-to-text-pdfminer", tags=["PDF Extraction"])
async def extract_text_from_pdfminer(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    contents = await file.read()
    try:
        text = pdf_service.extract_text_pdfminer(contents)
        return {"file_name": file.filename, "extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")
