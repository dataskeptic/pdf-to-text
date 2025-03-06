import fitz
import pdfplumber
from io import BytesIO
from pdfminer.high_level import extract_text
import re
from typing import Dict, Any

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

def parse_vehicle_document(text: str) -> Dict[str, Any]:
    """Parse Brazilian vehicle document information with targeted extraction"""
    patterns = {
        "codigo_renavam": r"CÓDIGO RENAVAM\n(\d+)",
        "placa_exercicio": r"PLACA EXERCÍCIO\n(\S+)\s(\d{4})",
        "cpf": r"CPF / CNPJ\n(\d{3}\.\d{3}\.\d{3}-\d{2})",
        "numero_crv": r"NÚMERO DO CRV\n(\d+)",
        "codigo_seguranca_cla": r"CÓDIGO DE SEGURANÇA DO CLA\n(\d+)",
        "marca_modelo": r"MARCA / MODELO / VERSÃO\n(.+?)\n",
        "cor_predominante": r"COR PREDOMINANTE\n(\S+)",
        "combustivel": r"COMBUSTÍVEL\n(\S+)",
        "renavam": r"RENAVAM\n(\d+)",
        "chassi": r"CHASSI\n(\S+)",
        "data_emissao": r"Documento emitido por .+? em (\d{2}/\d{2}/\d{4}) às (\d{2}:\d{2}:\d{2})",
        "categoria": r"CATEGORIA\n(.+?)\n",
        "nome_proprietario": r"NOME\n(.+?)\n",
        "ano_fabricacao": r"ANO FABRICAÇÃO\n(\d{4})",
        "ano_modelo": r"ANO MODELO\n(\d{4})"
    }

    structured_data = {}
    
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            # Handle multiple capture groups
            if len(match.groups()) > 1:
                structured_data[key] = {
                    "placa": match.group(1),
                    "ano": match.group(2)
                } if key == "placa_exercicio" else {
                    "data": match.group(1),
                    "hora": match.group(2)
                }
            else:
                structured_data[key] = match.group(1)

    # Additional processing for special cases
    if 'marca_modelo' in structured_data:
        parts = structured_data['marca_modelo'].split('/')
        structured_data.update({
            "marca": parts[0].strip(),
            "modelo": parts[1].strip() if len(parts) > 1 else None,
            "versao": parts[2].strip() if len(parts) > 2 else None
        })
        del structured_data['marca_modelo']

    return structured_data