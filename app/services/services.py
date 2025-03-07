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
    extracted_text = "\n".join(page.get_text() for page in pdf_document)
    return extracted_text.strip()

def extract_text_pdfplumber(contents: bytes) -> str:
    # Use BytesIO to convert bytes to a file-like object
    with BytesIO(contents) as pdf_file:
        with pdfplumber.open(pdf_file) as pdf:
            extracted_text = ""
            for page in pdf.pages:
                extracted_text += page.extract_text(x_tolerance=3, x_tolerance_ratio=None, y_tolerance=3, layout=False, x_density=7.25, y_density=13, line_dir_render=None, char_dir_render=None) or ""
                extracted_text += "\n\n"
   

    return extracted_text.strip()


def extract_tables_pdfplumber(contents: bytes):
    with pdfplumber.open(BytesIO(contents)) as pdf:
        for i, page in enumerate(pdf.pages):
            table = page.extract_table()  # Extracts a table as a list of lists
            if table:
                print(f"🟢 Table found on page {i+1}")
                for row in table:
                    print(row)
            else:
                print(f"❌ No table found on page {i+1}")


def extract_text_pdfminer(contents: bytes) -> str:
    # Use BytesIO to create a file-like object for pdfminer
    with BytesIO(contents) as pdf_file:
        text = extract_text(pdf_file)
    return text.strip()

def parse_vehicle_document(text: str) -> Dict[str, Any]:
    """Parse Brazilian vehicle document information with targeted extraction"""
    patterns = {
        "codigo_renavam": r"código renavam\n(\d+)",
        "placa_exercicio": r"placa exercício\n(\S+)\s(\d{4})",
        "cpf": r"cpf / cnpj\n(\d{3}\.\d{3}\.\d{3}-\d{2})",
        "numero_crv": r"número do crv\n(\d+)",
        "codigo_seguranca_cla": r"código de segurança do cla cat local data\n(\d+)",
        "local": r"código de segurança do cla cat local data\n\d+\s+\*\*\*\s+(.+?)\s+\d{2}/\d{2}/\d{4}",
        "data": r"código de segurança do cla cat local data\n\d+\s+\*\*\*\s+.+?\s+(\d{2}/\d{2}/\d{4})",
        "marca_modelo": r"marca / modelo / versão\n(.+?)\n",
        "cor_predominante": r"cor predominante\n(\S+)",
        "combustivel": r"combustível\n(\S+)",
        "renavam": r"renavam\n(\d+)",
        "chassi": r"chassi\n(?:.*\n)*?.*?([a-zA-Z0-9]{17})",
        "data_emissao": r"documento emitido por .+? em (\d{2}/\d{2}/\d{4}) às (\d{2}:\d{2}:\d{2})",
        "categoria": r"categoria\n(.+?)\n",
        "nome_proprietario": r"nome\n(.+?)\n",
        "ano_fabricacao": r"ano fabricação\n(\d{4})",
        "ano_modelo": r"ano modelo\n(\d{4})"
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


def parse_medical_certificate(text: str) -> Dict[str, Any]:
    """Parse Brazilian medical certificate information with targeted extraction"""
    
    patterns = {
        "paciente_nome": r"atesto, para os devidos fins, que\s+([\w\s]+)\s+\(cpf:",  # Extracts patient name
        "cpf": r"cpf:\s*(\d{3}\.\d{3}\.\d{3}-\d{2})",  # Extract CPF
        "medico_nome": r"crm\s*-\s*[a-zA-Z]+\s*\d{3}\s*\n(.+?)\ncrm\s*-\s*[a-zA-Z]+\s*\d{4}",  # Extracts name between the two CRMs
        "crm": r"crm\s*-\s*([a-zA-Z]+)\s*(\d{4})",  # Extract CRM (with state and number)
        "cid_10": r"cid-10:\s*([a-zA-Z0-9]+)",  # Extract CID-10 code
        "data_emissao": r"teresina,\s*(\d{2}/\d{2}/\d{4})\s*(\d{2}:\d{2}:\d{2})"  # Extract date and time
    }

    structured_data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) > 1:
                structured_data[key] = {
                    "data": match.group(1),
                    "hora": match.group(2)
                } if key == "data_emissao" else f"{match.group(1)}-{match.group(2)}"
            else:
                structured_data[key] = match.group(1).strip()

    return structured_data



def parse_cpf_document(text: str) -> Dict[str, Any]:
    """Parse Brazilian CPF document information with targeted extraction"""
    
    patterns = {
        "cpf": r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b",  # Matches CPF format 000.000.000-00
        "nome": r"nome\s*\n*([\w\s]+?)\n",  # Captures name after "nome" (handles extra spaces/newlines)
        "nascimento": r"nascimento\s*\n*(\d{2}/\d{2}/\d{4})"  # Matches date format DD/MM/YYYY
    }

    structured_data = {}

    for key, pattern in patterns.items():
        match = re.findall(pattern, text, re.IGNORECASE)  # Use findall() to prevent missing group errors
        structured_data[key] = match[0].strip() if match else None  # Return None instead of throwing an error

    return structured_data
