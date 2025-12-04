from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Product(BaseModel):
    name: str
    quantity: float
    unit_price: float
    total: float

class ExtractedData(BaseModel):
    vendor_name: str
    amount: float
    products: List[Product]
    total_amount: float
    date: Optional[datetime]
    document_type: str  # "invoice" or "receipt"

class Invoice(BaseModel):
    id: Optional[int] = None
    vendor_name: str
    amount: float
    products: List[Product]
    total_amount: float
    date: datetime
    created_at: datetime = datetime.now()

class Receipt(BaseModel):
    id: Optional[int] = None
    vendor_name: str
    amount: float
    products: List[Product]
    total_amount: float
    date: datetime
    created_at: datetime = datetime.now()