from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("Missing OpenAI API Key.")

client = OpenAI(api_key=OPENAI_API_KEY)

CACHE_FILE = "pdf_cache.json"


class OptimizationResponse(BaseModel):
    python_code: str
    reasoning: str


def get_pdf_file_id(pdf_path="instructions.pdf"):
    """Get the cached file_id if available, otherwise upload PDF once."""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
                if "file_id" in data and data["file_id"]:
                    print(f"[CACHE] Using cached file_id: {data['file_id']}")
                    return data["file_id"]

        print(f"[UPLOAD] Uploading PDF: {pdf_path}")
        with open(pdf_path, "rb") as f:
            pdf_file = client.files.create(file=f, purpose="user_data")

        print(f"[UPLOAD SUCCESS] File ID: {pdf_file.id}")
        with open(CACHE_FILE, "w") as f:
            json.dump({"file_id": pdf_file.id}, f)

        return pdf_file.id

    except Exception as e:
        print(f"[ERROR] PDF upload failed: {e}")
        raise



def generate_optimization(model, prompt, conversation_id):
    """Generate optimized Python code using PDF-based natural-language instructions."""

    try:
        file_id = get_pdf_file_id()

        response = client.responses.parse(
            model=model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_file", "file_id": file_id},
                        {"type": "input_text", "text": prompt},
                    ],
                }
            ],
            conversation=conversation_id,
            text_format=OptimizationResponse,
        )

        print(response.output_parsed)
        return response.output_parsed

    except Exception as e:
        return f"OpenAI API Error: {str(e)}"
