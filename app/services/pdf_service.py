import fitz
import pdfplumber
from io import BytesIO
from pdfminer.high_level import extract_text

def extract_text_fitz(pdf_bytes: bytes) -> str:
    # Open the PDF file using PyMuPDF (fitz)
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    # Extract text from each page
    text = "\n".join(page.get_text() for page in pdf_document)
    return text

def extract_text_pdfplumber(contents: bytes) -> str:
    # Use BytesIO to convert bytes to a file-like object
    with BytesIO(contents) as pdf_file:
        with pdfplumber.open(pdf_file) as pdf:
            extracted_text = ""
            for page in pdf.pages:
                # Ensure we handle pages that might not return text
                page_text = page.extract_text() or ""
                extracted_text += page_text + "\n\n"
    return extracted_text.strip()

def extract_text_pdfminer(contents: bytes) -> str:
    # Use BytesIO to create a file-like object for pdfminer
    with BytesIO(contents) as pdf_file:
        text = extract_text(pdf_file)
    return text.strip()
