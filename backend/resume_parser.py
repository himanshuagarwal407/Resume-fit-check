import os
import pdfplumber
from docx import Document

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=1)
            if page_text:
                text += page_text + "\n"
    
    return text

def extract_text_from_docx(file_path: str) -> str:
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def extract_resume_text(file_path: str) -> str:
    _, extension = os.path.splitext(file_path)
    extension = extension.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)
    elif extension == ".docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

if __name__ == "__main__":
    # Example usage
    file_path = "software-engineer-doc-resume-template.docx"
    extracted_text = extract_resume_text(file_path)
    print(f"Length of extracted text: {len(extracted_text)}")
    print("---START---")
    print(extracted_text)
    print("---END---")