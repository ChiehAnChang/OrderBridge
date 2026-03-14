import base64
import json
import os
import re
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile
from openai import OpenAI

from app.services.image_gen import generate_food_image, generate_image_prompt

router = APIRouter(prefix="/ocr", tags=["OCR"])

OUTDIR = Path("outputs")

EXTRACT_PROMPT = """Extract all food items from this menu image.
Return ONLY valid JSON in this format:
{
  "items": [{"name": "...", "description": "...", "halal": "yes/no/unknown"}],
  "cultural_flags": []
}
cultural_flags should list any pork, alcohol, shellfish, or other non-halal ingredients detected (e.g. "pork detected"). If none found, return an empty array."""


def _get_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("HF_TOKEN", ""),
        base_url=os.getenv(
            "HF_BASE_URL",
            "https://router.huggingface.co/v1",
        ),
    )


def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw, flags=re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}


def _slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-+", "-", text).strip("-") or "item"


@router.post("")
def ocr_menu(request: Request, file: UploadFile = File(...)):
    client = _get_client()
    chat_model = os.getenv("HF_MODEL_NAME", "Qwen/Qwen3-VL-8B-Instruct")
    hf_endpoint = os.getenv(
        "HF_IMAGE_ENDPOINT",
        "https://jjx1c75qu4j1zt5s.us-east-1.aws.endpoints.huggingface.cloud",
    )

    # Encode image as base64
    image_bytes = file.file.read()
    b64 = base64.b64encode(image_bytes).decode()
    mime = file.content_type or "image/jpeg"

    # Extract menu items via vision
    resp = client.chat.completions.create(
        model=chat_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime};base64,{b64}"},
                    },
                    {"type": "text", "text": EXTRACT_PROMPT},
                ],
            }
        ],
        max_tokens=800,
    )

    raw = resp.choices[0].message.content or "{}"
    data = _parse_json(raw)

    items = data.get("items", [])
    cultural_flags = data.get("cultural_flags", [])

    OUTDIR.mkdir(parents=True, exist_ok=True)

    result_items = []
    for item in items:
        name = item.get("name", "item")
        slug = _slugify(name)
        output_path = OUTDIR / f"{slug}.png"

        if not output_path.exists():
            prompt = generate_image_prompt(client, chat_model, item)
            generate_food_image(prompt, hf_endpoint, output_path)

        image_url = str(request.base_url) + f"static/{slug}.png" if output_path.exists() else None
        result_items.append({"name": name, "image_url": image_url})

    return {"items": result_items, "cultural_flags": cultural_flags}
