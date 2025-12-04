from src.extractors.invoice_extractor import extract_invoice_data
from src.extractors.receipt_extractor import extract_receipt_data
from src.types.schemas import ExtractedData

def extraction_agent(document_text: str, document_type: str) -> ExtractedData:
    """Route document to appropriate extractor"""
    
    if document_type.lower() == "invoice":
        return extract_invoice_data(document_text)
    elif document_type.lower() == "receipt":
        return extract_receipt_data(document_text)
    else:
        raise ValueError(f"Unknown document type: {document_type}")