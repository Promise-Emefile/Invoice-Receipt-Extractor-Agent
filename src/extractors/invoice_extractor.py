# ...existing code...
import os
import json
from typing import Any, Dict

def _parse_response_text(raw: str) -> Dict[str, Any]:
    raw = (raw or "").strip()
    try:
        return json.loads(raw)
    except Exception:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end])
            except Exception:
                pass
    raise ValueError("LLM response did not contain valid JSON")

def extract_invoice_data(document_text: str):
    """
    Extract structured invoice data from text.
    Uses LangChain ChatOpenAI if available; otherwise falls back to openai client.
    Returns a dict or a pydantic ExtractedData instance when available.
    """
    prompt = f"""Extract invoice information from the following text.

Return a JSON object with:
- vendor_name (string)
- amount (float)
- products (list of {{name, quantity, unit_price, total}})
- total_amount (float)
- date (string or null)

Document:
{document_text}

JSON Response:"""

    # Try LangChain first (avoid imports that may not exist)
    try:
        try:
            from langchain.chat_models import ChatOpenAI  # common import
        except Exception:
            from langchain_openai import ChatOpenAI  # older wrapper

        llm = ChatOpenAI(model="gpt-4o-mini")
        # try common calling patterns
        try:
            response = llm.invoke([{"role": "user", "content": prompt}])
            raw = getattr(response, "content", None) or getattr(response, "text", None) or str(response)
        except Exception:
            response = llm([{"role": "user", "content": prompt}])
            raw = getattr(response, "content", None) or getattr(response, "text", None) or str(response)

        data = _parse_response_text(raw)
    except ModuleNotFoundError:
        # fallback to openai
        try:
            import openai
        except Exception as e:
            raise ImportError(
                "Neither langchain nor openai is available. Install with: python -m pip install langchain openai"
            ) from e

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                openai.api_key = api_key
            except Exception:
                pass

        # try legacy ChatCompletion
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            raw = resp["choices"][0]["message"]["content"]
            data = _parse_response_text(raw)
        except Exception:
            # try newer OpenAI client
            try:
                from openai import OpenAI
                client = OpenAI()
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0
                )
                raw = resp.choices[0].message.content
                data = _parse_response_text(raw)
            except Exception as e2:
                raise RuntimeError("Failed to call LLM via openai client") from e2

    # Try to return a pydantic model if available
    try:
        from src.types.schemas import ExtractedData
        products = data.get("products", [])
        return ExtractedData(
            vendor_name=data.get("vendor_name"),
            amount=data.get("amount"),
            products=products,
            total_amount=data.get("total_amount"),
            date=data.get("date"),
            document_type="invoice"
        )
    except Exception:
        return {
            "vendor_name": data.get("vendor_name"),
            "amount": data.get("amount"),
            "products": data.get("products", []),
            "total_amount": data.get("total_amount"),
            "date": data.get("date"),
            "document_type": "invoice"
        }
# ...existing code...