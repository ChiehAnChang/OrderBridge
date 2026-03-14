import io
import requests
from pathlib import Path
from typing import Optional

from openai import OpenAI
from PIL import Image


def generate_image_prompt(client: OpenAI, chat_model: str, item: dict) -> str:
    name = item.get("name", "food item")
    description = item.get("description", "")
    resp = client.chat.completions.create(
        model=chat_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a food image prompt generator. "
                    "Return ONLY a 1-2 sentence realistic visual description of the dish "
                    "for image generation. No text, labels, UI, or watermarks."
                ),
            },
            {
                "role": "user",
                "content": f"Food: {name}. Description: {description}.",
            },
        ],
        max_tokens=150,
        temperature=0.4,
    )
    return (resp.choices[0].message.content or f"Realistic food photo of {name}.").strip()


def generate_food_image(prompt: str, hf_endpoint: str, output_path: Path) -> Optional[str]:
    try:
        response = requests.post(
            hf_endpoint,
            headers={"Accept": "image/png", "Content-Type": "application/json"},
            json={"inputs": prompt, "parameters": {}},
        )
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        image.save(output_path)
        return str(output_path)
    except Exception as e:
        print(f"[WARN] Image generation failed for '{prompt[:40]}': {e}")
        return None
