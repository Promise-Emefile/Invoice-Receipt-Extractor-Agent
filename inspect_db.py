import sqlite3
import os

db_path = os.path.abspath("invoices.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("Invoices:")
try:
    for row in cur.execute("SELECT id, vendor_name, total_amount, date, file_path FROM invoices;"):
        print(row)
except Exception as e:
    print("Failed to read invoices:", e)

print("\nReceipts:")
try:
    for row in cur.execute("SELECT id, vendor_name, total_amount, date, file_path FROM receipts;"):
        print(row)
except Exception as e:
    print("Failed to read receipts (table may not exist):", e)

conn.close()