import pdfplumber

def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(x_tolerance=1)
            if page_text:
                text += page_text + "\n"
    
    return text

if __name__ == "__main__":
    # Example usage
    file_path = "Himanshu_Agarwal_React2.pdf"
    extracted_text = extract_text_from_pdf(file_path)
    print(f"Length of extracted text: {len(extracted_text)}")
    print("---START---")
    print(extracted_text)
    print("---END---")