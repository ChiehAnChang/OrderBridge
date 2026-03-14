import os
import base64
import mimetypes
import argparse
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def file_to_data_url(path: str) -> str:
    mime_type, _ = mimetypes.guess_type(path)
    if mime_type is None:
        mime_type = "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime_type};base64,{b64}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Path to menu image")
    parser.add_argument(
        "--model",
        default=os.getenv("HF_MODEL_NAME", "Qwen/Qwen3.5-397B-A17B"),
        help="Hugging Face routed model name",
    )
    args = parser.parse_args()

    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN is not set in the environment.")

    client = OpenAI(
        base_url=os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1"),
        api_key=hf_token.strip(),
    )

    image_data_url = file_to_data_url(args.image)

    completion = client.chat.completions.create(
        model=args.model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a menu understanding assistant. "
                    "Extract the main visible dishes or set meals from a restaurant menu image. "
                    "Be concise."
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Read this menu image and list the main dishes or set meals. "
                            'Return JSON only in this format: '
                            '{"items":[{"name":"string","category":"string","price":"string or null"}]}'
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        },
                    },
                ],
            },
        ],
    )

    print(completion.choices[0].message.content)


if __name__ == "__main__":
    main()