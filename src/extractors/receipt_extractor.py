# ...existing code...
"""
Receipt extractor with lazy imports and fallback to the OpenAI client if LangChain
components aren't available. This avoids import-time failures and gives a clear
error message when dependencies are missing.
"""
import json
import os
from typing import Any, Dict

def _parse_response_text(raw: str) -> Dict[str, Any]:
    # attempt to parse JSON from the LLM output
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        # try to locate a JSON block in the text
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start:end])
            except Exception:
                pass
    raise ValueError("LLM response did not contain valid JSON")

def extract_receipt_data(document_text: str):
    """
    Extract structured data from a receipt text.
    Tries to use LangChain if available; otherwise falls back to openai.ChatCompletion.
    Returns either a dict or a pydantic ExtractedData instance when available.
    """
    prompt_template = """Extract receipt information from the following text.

Return a JSON object with:
- vendor_name (string)
- amount (float)
- products (list of {{name, quantity, unit_price, total}})
- total_amount (float)
- date (string or null)

Document:
{document_text}

JSON Response:""".format(document_text=document_text)

    # Try LangChain first (some versions expose different import paths)
    try:
        try:
            from langchain.chat_models import ChatOpenAI  # new-style import
        except Exception:
            from langchain_openai import ChatOpenAI  # older package wrapper

        try:
            from langchain.prompts import PromptTemplate
        except Exception:
            # PromptTemplate may be in different locations on very old/new versions;
            # we don't strictly need it here since we assemble the prompt manually.
            PromptTemplate = None  # type: ignore

        llm = ChatOpenAI(model="gpt-4o-mini")
        # LangChain wrapper APIs differ; try a couple of common ways:
        try:
            # some ChatOpenAI objects allow a simple call with messages or text
            response = llm.invoke([{"role": "user", "content": prompt_template}])
            raw = getattr(response, "content", None) or getattr(response, "text", None) or str(response)
        except Exception:
            # fallback: call llm with direct call if supported
            response = llm([{"role": "user", "content": prompt_template}])
            raw = getattr(response, "content", None) or getattr(response, "text", None) or str(response)

        data = _parse_response_text(raw)
    except ModuleNotFoundError:
        # LangChain not installed, fallback to openai
        try:
            import openai
        except Exception as e:
            raise ImportError(
                "Neither langchain nor openai client is available in this environment. "
                "Install with: python -m pip install langchain openai"
            ) from e

        # ensure API key is set
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY".lower())
        if api_key:
            try:
                openai.api_key = api_key
            except Exception:
                pass

        # Use legacy openai.ChatCompletion if available
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt_template}],
                temperature=0
            )
            raw = resp["choices"][0]["message"]["content"]
            data = _parse_response_text(raw)
        except Exception as e:
            # Newer openai client variants may use OpenAI() client
            try:
                from openai import OpenAI
                client = OpenAI()
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_template}],
                    temperature=0
                )
                raw = resp.choices[0].message.content
                data = _parse_response_text(raw)
            except Exception as e2:
                raise RuntimeError(
                    "Failed to call LLM via openai client. Original error: "
                    f"{e}; fallback error: {e2}"
                ) from e2

    # Try to return a pydantic model if available
    try:
        from src.types.schemas import ExtractedData, Product
        products = data.get("products", [])
        # normalize product items to list of dicts if necessary
        normalized_products = []
        for p in products:
            if isinstance(p, dict):
                normalized_products.append(p)
            else:
                normalized_products.append({"name": str(p), "quantity": 1, "unit_price": 0.0, "total": 0.0})
        return ExtractedData(
            vendor_name=data.get("vendor_name"),
            amount=data.get("amount"),
            products=normalized_products,
            total_amount=data.get("total_amount"),
            date=data.get("date"),
            document_type="receipt"
        )
    except Exception:
        # return raw dict if ExtractedData is unavailable
        return {
            "vendor_name": data.get("vendor_name"),
            "amount": data.get("amount"),
            "products": data.get("products", []),
            "total_amount": data.get("total_amount"),
            "date": data.get("date"),
            "document_type": "receipt"
        }
# ...existing code...