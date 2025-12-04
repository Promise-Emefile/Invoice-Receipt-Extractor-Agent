# Invoice \& Receipt Agent



A small, practical tool that reads invoices and receipts (PDFs or images), extracts structured data using OCR + an LLM, and stores both the original file and structured results in a local SQLite database.



This README explains what the project does, how it works and how to run it on Windows.



## TL;DR — what this does

Drop a PDF or image into the program and it extracts vendor, line items, amounts and date, saves the original file in `uploads/` and writes structured records to `invoices.db`.



## Why this exists

Manually processing invoices is slow and error-prone. This project automates that step by combining:

- fast text extraction for digital PDFs,

- OCR for scanned images,

- an LLM to interpret messy invoice text into a predictable JSON,

- a small database to keep results and the original file for auditing.



It’s designed to be clear, auditable, and easy to explain.



## Quick start (Windows)



1. Open PowerShell and activate your environment :

&nbsp;  ```powershell

&nbsp;  conda activate "your environment"

&nbsp;  ```



2. Install Python dependencies if you haven’t:

&nbsp;  ```powershell

&nbsp;  python -m pip install -r requirements.txt

&nbsp;  ```



3. Install system binaries (Poppler + Tesseract) — conda recommended:

&nbsp;  ```powershell

&nbsp;  conda install -c conda-forge poppler tesseract

&nbsp;  ```



4. Add your OpenAI key to a `.env` file in the project root:

&nbsp;  ```

&nbsp;  OPENAI\_API\_KEY=sk-...

&nbsp;  DATABASE\_URL=sqlite:///./invoices.db

&nbsp;  POPPLER\_PATH=C:\\path\\to\\poppler\\bin   # optional if conda put poppler on PATH

&nbsp;  TESSERACT\_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe  # optional

&nbsp;  ```



5. Run the program with a file:

&nbsp;  ```powershell

&nbsp;  # from project root

&nbsp;  python -m src.main "C:\\full\\path\\to\\invoice.pdf" invoice

&nbsp;  ```



6. Inspect saved rows:

&nbsp;  ```powershell

&nbsp;  python inspect\_db.py

&nbsp;  ```



## Project layout

- `src/main.py` — orchestrates the pipeline: copy file → extract text → run extractor → save result

- `src/utils/helpers.py` — pdfminer + pdf2image/pytesseract helpers for text extraction

- `src/agents/extraction\_agent.py` — chooses invoice vs receipt extractor

- `src/extractors/\*.py` — builds prompt, calls LLM (LangChain if available, otherwise OpenAI), returns JSON

- `src/agents/processing\_agent.py` — normalizes data (dates, products), writes to DB

- `src/database/\*.py` — SQLAlchemy models and DB connection

- `src/types/schemas.py` — Pydantic shapes for extracted data

- `uploads/` — copies of processed files

- `invoices.db` — default SQLite database file (created in project root)



---



## How it works

1. main copies the file to `uploads/` (so the original is kept).

2. helpers extract text:

&nbsp;  - try `pdfminer` (fast) for text PDFs

&nbsp;  - if empty or fails, use `pdf2image` → images → `pytesseract` OCR (works for scans)

3. extraction\_agent calls the document-specific extractor that:

&nbsp;  - builds a prompt that requests a strict JSON format

&nbsp;  - calls an LLM (LangChain wrapper or direct OpenAI)

&nbsp;  - parses JSON into a Pydantic model or a dict

4. processing\_agent normalizes fields (parse date to datetime, convert product list to JSON string) and inserts a row into `invoices` table



## Helpful commands (Windows / PowerShell)



\- Run the app:

&nbsp; ```powershell

&nbsp; python -m src.main "C:\\path\\to\\file.pdf" invoice

&nbsp; ```



- Inspect DB:

&nbsp; ```powershell

&nbsp; python inspect\_db.py

&nbsp; ```



- Recreate DB (dev only):

&nbsp; ```powershell

&nbsp; Remove-Item .\\invoices.db -Force

&nbsp; python -m src.main "C:\\path\\to\\file.pdf" invoice

&nbsp; ```



- Install system OCR tools (conda):

&nbsp; ```powershell

&nbsp; conda install -c conda-forge poppler tesseract

&nbsp; ```





