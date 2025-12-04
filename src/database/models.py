from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class InvoiceModel(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True)
    vendor_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    products = Column(JSON, nullable=False)
    total_amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    file_path = Column(String, nullable=True)  # <-- added

class ReceiptModel(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True)
    vendor_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    products = Column(JSON, nullable=False)
    total_amount = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    file_path = Column(String, nullable=True)  # <-- added