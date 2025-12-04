from typing import Optional, Any
import json
from datetime import datetime, date
from src.types.schemas import ExtractedData
from src.database.connection import SessionLocal
from src.database.models import InvoiceModel, ReceiptModel

# optional: nicer parsing if python-dateutil is installed
try:
    from dateutil import parser as date_parser  # type: ignore
except Exception:
    date_parser = None  # fallback to manual formats

def _parse_date(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    if date_parser:
        try:
            return date_parser.parse(str(value))
        except Exception:
            pass
    # try common formats
    formats = ("%Y-%m-%d", "%d %b %Y", "%d %B %Y", "%m/%d/%Y", "%d/%m/%Y")
    for fmt in formats:
        try:
            return datetime.strptime(str(value), fmt)
        except Exception:
            continue
    # last resort: try numeric timestamp
    try:
        ts = float(value)
        return datetime.fromtimestamp(ts)
    except Exception:
        return None

def processing_agent(extracted_data: ExtractedData, source_file_path: Optional[str] = None) -> dict:
    """Process and validate extracted data, then save to database."""
    db = SessionLocal()
    try:
        # normalize products to list of dicts
        if hasattr(extracted_data, "products"):
            products = extracted_data.products
        else:
            products = extracted_data.get("products", [])
        products_json = json.dumps([p.dict() if hasattr(p, "dict") else p for p in products])

        # normalize doc_type and common fields
        doc_type = (getattr(extracted_data, "document_type", None)
                    or extracted_data.get("document_type", "")).lower()

        vendor = getattr(extracted_data, "vendor_name", None) or extracted_data.get("vendor_name")
        amount = getattr(extracted_data, "amount", None) or extracted_data.get("amount")
        total_amount = getattr(extracted_data, "total_amount", None) or extracted_data.get("total_amount")
        raw_date = getattr(extracted_data, "date", None) or extracted_data.get("date")
        parsed_date = _parse_date(raw_date)

        common_kwargs = dict(
            vendor_name=vendor,
            amount=amount,
            products=products_json,
            total_amount=total_amount,
            date=parsed_date if parsed_date is not None else datetime.now(),
            file_path=source_file_path
        )

        if doc_type == "invoice":
            record = InvoiceModel(**common_kwargs)
        elif doc_type == "receipt":
            record = ReceiptModel(**common_kwargs)
        else:
            return {"status": "error", "message": f"Unknown document_type: {doc_type}"}

        db.add(record)
        db.commit()
        db.refresh(record)
        return {"status": "success", "type": doc_type, "id": record.id}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()