import io
import os
from dotenv import load_dotenv

load_dotenv()
import json
import argparse
import re
import requests
from pathlib import Path
from typing import Any, Dict, Optional

from openai import OpenAI
from PIL import Image


def normalize_halal(value: Any) -> str:
    """
    Normalize halal field to one of: yes / no / unknown.
    English-only normalization.
    """
    if value is None:
        return "unknown"

    text = str(value).strip().lower()

    yes_values = {"yes", "y", "true", "halal"}
    no_values = {"no", "n", "false", "not halal"}
    unknown_values = {"unknown", "unk", "?", ""}

    if text in yes_values:
        return "yes"
    if text in no_values:
        return "no"
    if text in unknown_values:
        return "unknown"

    return "unknown"


def slugify(text: str) -> str:
    """
    Convert text into a simple filename-safe slug.
    """
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text or "menu-item"


def build_order_sentence(name: str, halal: str) -> str:
    """
    Build the short ordering sentence based on halal status.
    """
    base = f"May I have the {name}, please?"

    if halal == "yes":
        return f"{base} Thank you."
    if halal == "no":
        return f"{base} Do you have a halal version?"
    return f"{base} Is this halal?"


def build_system_prompt() -> str:
    return (
        "You are a helpful assistant for a restaurant ordering support app. "
        "The user provides structured menu item information extracted from a menu. "
        "Your task is to create a simple, realistic, appetizing image-generation prompt "
        "for the menu item, suitable for helping a newcomer identify what to order. "
        "You must also return a short visual card title and 3-6 simple visual tags. "
        "Do not mention text overlays, labels, menus, watermarks, logos, or UI. "
        "Keep the food appearance realistic and culturally neutral unless the item clearly implies a cuisine."
    )


def build_user_prompt(item: Dict[str, Any], order_sentence: str) -> str:
    """
    Ask the LLM to return a strict JSON object.
    """
    return f"""
Here is a structured menu item object:

{json.dumps(item, ensure_ascii=False, indent=2)}

The short order sentence is:
{order_sentence}

Return ONLY valid JSON with the following schema:
{{
  "card_title": "short title for the order card",
  "image_prompt": "a realistic food image generation prompt for this menu item",
  "visual_tags": ["tag1", "tag2", "tag3"]
}}

Rules:
1. card_title should be short and easy to understand.
2. image_prompt should describe the dish visually in plain English, focusing on how it looks.
3. image_prompt must avoid mentioning text, captions, labels, menu, watermark, poster, or collage.
4. visual_tags should be simple concrete words or short phrases, 3 to 6 items.
5. If item details are incomplete, infer conservatively from the item name and description.
6. Output JSON only, with no markdown fences.
""".strip()


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Parse JSON robustly from raw model output.
    """
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        candidate = match.group(0)
        return json.loads(candidate)

    raise ValueError("Could not parse JSON from model response.")


def generate_structured_card_content(
    client: OpenAI,
    chat_model: str,
    item: Dict[str, Any],
    max_tokens: int = 500,
) -> Dict[str, Any]:
    """
    Call chat completion model to generate:
    - card_title
    - image_prompt
    - visual_tags
    """
    name = item.get("name", "this item")
    halal = normalize_halal(item.get("halal"))
    order_sentence = build_order_sentence(name, halal)

    resp = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": build_user_prompt(item, order_sentence)},
        ],
        max_tokens=max_tokens,
        temperature=0.4,
    )

    raw_text = resp.choices[0].message.content or ""
    parsed = extract_json_from_text(raw_text)

    return {
        "card_title": parsed.get("card_title", str(name).title()),
        "image_prompt": parsed.get("image_prompt", f"Realistic food photo of {name}."),
        "visual_tags": parsed.get("visual_tags", []),
        "order_sentence": order_sentence,
        "halal_normalized": halal,
        "raw_model_output": raw_text,
    }


def try_generate_image_hf(
    endpoint_url: str,
    prompt: str,
    output_path: Path,
) -> Optional[str]:
    """
    Generate an image using a HuggingFace dedicated inference endpoint.
    Returns saved file path if successful, else None.
    """
    try:
        response = requests.post(
            endpoint_url,
            headers={"Accept": "image/png", "Content-Type": "application/json"},
            json={"inputs": prompt, "parameters": {}},
        )
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content))
        image.save(output_path)
        return str(output_path)
    except Exception as e:
        print(f"[WARN] Hugging Face image generation failed: {e}")
        return None


def load_item_from_input(input_path: Optional[str], inline_json: Optional[str]) -> Dict[str, Any]:
    """
    Load item dict from a JSON file or inline JSON string.
    """
    if input_path:
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    if inline_json:
        return json.loads(inline_json)

    raise ValueError("Please provide either --input or --json.")


def enrich_item(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean and normalize the input object.
    """
    if "name" not in item or not str(item["name"]).strip():
        raise ValueError("Input item must include a non-empty 'name' field.")

    item = dict(item)
    item["name"] = str(item["name"]).strip()
    item["halal"] = normalize_halal(item.get("halal"))

    if "ingredients" in item and not isinstance(item["ingredients"], list):
        item["ingredients"] = [str(item["ingredients"])]

    return item


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate menu-item image prompt, order sentence, and optionally an image."
    )
    parser.add_argument("--input", type=str, help="Path to input JSON file containing one menu item")
    parser.add_argument("--json", type=str, help="Inline JSON string for one menu item")
    parser.add_argument("--outdir", type=str, default="outputs", help="Output directory")
    parser.add_argument("--no-image", action="store_true", help="Skip image generation")
    parser.add_argument("--max-tokens", type=int, default=500, help="Max tokens for chat completion")
    args = parser.parse_args()

    # LLM settings (still using your OpenAI-compatible endpoint)
    api_key = os.getenv("OPENAI_API_KEY", "test")
    base_url = os.getenv(
        "OPENAI_BASE_URL",
        "https://vjioo4r1vyvcozuj.us-east-2.aws.endpoints.huggingface.cloud/v1",
    )
    chat_model = os.getenv("CHAT_MODEL", "openai/gpt-oss-120b")

    # Hugging Face image generation settings
    hf_image_endpoint = os.getenv(
        "HF_IMAGE_ENDPOINT",
        "https://jjx1c75qu4j1zt5s.us-east-1.aws.endpoints.huggingface.cloud",
    )

    print("OPENAI_API_KEY =", api_key)
    print("OPENAI_BASE_URL =", base_url)
    print("CHAT_MODEL =", chat_model)
    print("HF_IMAGE_ENDPOINT =", hf_image_endpoint)

    client = OpenAI(api_key=api_key, base_url=base_url)

    item = load_item_from_input(args.input, args.json)
    item = enrich_item(item)

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    slug = slugify(item["name"])
    json_output_path = outdir / f"{slug}_card.json"
    image_output_path = outdir / f"{slug}.png"

    result = generate_structured_card_content(
        client=client,
        chat_model=chat_model,
        item=item,
        max_tokens=args.max_tokens,
    )

    final_output = {
        "input_item": item,
        "card_title": result["card_title"],
        "image_prompt": result["image_prompt"],
        "visual_tags": result["visual_tags"],
        "order_sentence": result["order_sentence"],
        "halal_normalized": result["halal_normalized"],
        "image_path": None,
    }

    if not args.no_image:
        image_path = try_generate_image_hf(
            endpoint_url=hf_image_endpoint,
            prompt=result["image_prompt"],
            output_path=image_output_path,
        )
        final_output["image_path"] = image_path

    save_json(final_output, json_output_path)

    print("\n=== Done ===")
    print(f"Card JSON saved to: {json_output_path}")
    if final_output["image_path"]:
        print(f"Image saved to: {final_output['image_path']}")
    else:
        print("No image saved.")

    print("\n=== Order Sentence ===")
    print(final_output["order_sentence"])

    print("\n=== Image Prompt ===")
    print(final_output["image_prompt"])

    print("\n=== Final Output JSON ===")
    print(json.dumps(final_output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
