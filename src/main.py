# ...existing code...
import os
import sys
import shutil
from dotenv import load_dotenv
from src.database.connection import init_db
from src.agents.extraction_agent import extraction_agent
from src.agents.processing_agent import processing_agent
from src.utils.helpers import extract_text_from_pdf, extract_text_from_image

load_dotenv()
init_db()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _get_field(obj, name, default=None):
    try:
        return getattr(obj, name)
    except Exception:
        try:
            return obj.get(name, default)
        except Exception:
            return default

def process_document(file_path: str, document_type: str):
    """Main pipeline: extract text → extract data → save to database"""
    file_path = os.path.abspath(file_path)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Document not found: {file_path}")

    # optional: copy uploaded file to uploads/ and use that copy
    dest = os.path.join(UPLOAD_DIR, f"{int(os.path.getmtime(file_path))}_{os.path.basename(file_path)}")
    shutil.copy2(file_path, dest)
    print(f"Stored uploaded file at: {dest}")

    print(f"Processing {document_type}...")
    
    # Step 1: Extract text from document
    if dest.lower().endswith(".pdf"):
        document_text = extract_text_from_pdf(dest)
    else:
        document_text = extract_text_from_image(dest)
    
    # Step 2: Extract structured data
    extracted_data = extraction_agent(document_text, document_type)

    # safe access for both pydantic models and dicts
    vendor = _get_field(extracted_data, "vendor_name", "<unknown>")
    total = _get_field(extracted_data, "total_amount", _get_field(extracted_data, "amount", "<unknown>"))
    print(f"✅ Extracted: {vendor} - ${total}")
    
    # Step 3: Process and save to database
    result = processing_agent(extracted_data, source_file_path=dest if 'source_file_path' in processing_agent.__code__.co_varnames else None)
    print(f"✅ Saved to database: {result}")
    
    return result

if __name__ == "__main__":
    # Usage:
    # python -m src.main <path-to-file> <invoice|receipt>
    if len(sys.argv) >= 3:
        path = sys.argv[1]
        doc_type = sys.argv[2]
    else:
        # fallback example (you can remove these defaults)
        path = "invoice.pdf"
        doc_type = "invoice"

    result = process_document(path, doc_type)
    print("Result:", result)
# ...existing code...