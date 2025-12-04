# ...existing code...
import os
from PIL import Image
import pytesseract

def extract_text_from_pdf(pdf_path: str) -> str:
    """Try pdfminer (text PDFs) first; if empty, fall back to pdf2image+Tesseract OCR."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {os.path.abspath(pdf_path)}")

    # try fast text extraction (no external binaries)
    try:
        from pdfminer.high_level import extract_text as pdfminer_extract_text
        text = pdfminer_extract_text(pdf_path)
        if text and text.strip():
            return text
    except Exception:
        pass

    # set TESSERACT_CMD or POPPLER_PATH via env if needed
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        import pdf2image
        poppler_path = os.getenv("POPPLER_PATH")
        if poppler_path:
            images = pdf2image.convert_from_path(pdf_path, poppler_path=poppler_path)
        else:
            images = pdf2image.convert_from_path(pdf_path)
    except pdf2image.exceptions.PDFInfoNotInstalledError:
        raise RuntimeError(
            "Poppler not found. Install poppler and add to PATH or set POPPLER_PATH.\n"
            "Conda (recommended): conda install -c conda-forge poppler\n"
            "Download: https://github.com/oschwartz10612/poppler-windows/releases"
        )
    except Exception as e:
        raise RuntimeError(f"Failed to convert PDF to images: {e}") from e

    text = ""
    for image in images:
        text += pytesseract.image_to_string(image)
    return text

# ...existing code...
def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image file using Tesseract OCR."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {os.path.abspath(image_path)}")

    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    image = Image.open(image_path)
    return pytesseract.image_to_string(image)
# ...existing code...