import zipfile
import re
from pypdf import PdfReader

def extract_docx_text(path):
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/document.xml').decode('utf-8')
            # Simple regex to strip xml tags and find text
            text = re.sub('<[^<]+>', '', xml_content)
            return text
    except Exception as e:
        return f"Error reading DOCX: {e}"

def extract_pdf_text(path):
    try:
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n---\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

print("--- DOCX CONTENT ---")
print(extract_docx_text('sample/Inputresume.docx')[:2000]) # Print first 2000 chars
print("\n--- PDF CONTENT ---")
print(extract_pdf_text('sample/OutputFile.pdf')[:2000])
