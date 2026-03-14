import re
from app.schemas import ClassificationResponse

# ---------- Intent rules (keyword patterns) ----------

INTENT_RULES: list[tuple[str, list[str]]] = [
    ("size_choice",          [r"\bsize\b", r"\bsmall\b", r"\bmedium\b", r"\blarge\b", r"\bregular\b"]),
    ("drink_choice",         [r"\bdrink\b", r"\bbeverage\b", r"\bjuice\b", r"\bsoda\b", r"\bwater\b", r"\bcoffee\b", r"\btea\b"]),
    ("combo_choice",         [r"\bcombo\b", r"\bmeal deal\b", r"\bset meal\b", r"\bwith fries\b"]),
    ("dine_in_takeout",      [r"\bfor here\b", r"\bto go\b", r"\btake.?out\b", r"\bdine.?in\b", r"\beat in\b", r"\btake away\b"]),
    ("spice_level",          [r"\bspic(y|e|iness)\b", r"\bmild\b", r"\bhow (hot|spicy)\b", r"\bextra hot\b", r"\bno spice\b"]),
    ("quantity_confirmation", [r"\bhow many\b", r"\bquantity\b", r"\bone or two\b", r"\bone\b.*\btwo\b", r"\bnumber\b"]),
    ("payment_question",     [r"\bpay\b", r"\bcash\b", r"\bcard\b", r"\bcredit\b", r"\bdebit\b", r"\btap\b", r"\bapple pay\b", r"\bgoogle pay\b"]),
    ("unavailable_item",     [r"\bsorry\b.*\bout\b", r"\bout of stock\b", r"\bnot available\b", r"\bwe('re| are) out\b", r"\bdon't have\b"]),
    ("clarification",        [r"\bpardon\b", r"\brepeat\b", r"\bsorry\b", r"\bdidn't (hear|catch|get)\b", r"\bcan you say\b"]),
]

# ---------- Templates per intent ----------

TEMPLATES: dict[str, dict] = {
    "size_choice": {
        "zh": "他在问你要什么尺寸",
        "suggested_responses": ["Small", "Medium", "Large"],
        "visual_hint": "size_options",
    },
    "drink_choice": {
        "zh": "他在问你要喝什么饮料",
        "suggested_responses": ["Water", "Coke", "Orange Juice", "No drink"],
        "visual_hint": "drink_options",
    },
    "combo_choice": {
        "zh": "他在问你要不要套餐",
        "suggested_responses": ["Yes, combo please", "No, just the item"],
        "visual_hint": "combo_options",
    },
    "dine_in_takeout": {
        "zh": "他在问你是在这里吃还是打包带走",
        "suggested_responses": ["For here", "To go"],
        "visual_hint": "dine_in_takeout",
    },
    "spice_level": {
        "zh": "他在问你要多辣",
        "suggested_responses": ["No spice", "Mild", "Medium", "Hot", "Extra hot"],
        "visual_hint": "spice_level",
    },
    "quantity_confirmation": {
        "zh": "他在问你要几份",
        "suggested_responses": ["1", "2", "3"],
        "visual_hint": "quantity",
    },
    "payment_question": {
        "zh": "他在问你怎么付款",
        "suggested_responses": ["Cash", "Credit card", "Debit card", "Apple Pay"],
        "visual_hint": "payment",
    },
    "unavailable_item": {
        "zh": "这个菜今天没有了",
        "suggested_responses": ["OK, I'll choose something else", "OK, thank you"],
        "visual_hint": "unavailable",
    },
    "clarification": {
        "zh": "他没听清楚，请重复一下",
        "suggested_responses": ["Could you repeat that?", "Please say it again"],
        "visual_hint": "clarification",
    },
    "other": {
        "zh": "服务员说了一些话，请确认",
        "suggested_responses": ["OK", "Yes", "No", "Please repeat"],
        "visual_hint": "general",
    },
}

# ---------- Intent icons ----------

INTENT_ICONS: dict[str, str] = {
    "size_choice":          "📏",
    "drink_choice":         "🥤",
    "combo_choice":         "🍱",
    "dine_in_takeout":      "🏠",
    "spice_level":          "🌶️",
    "quantity_confirmation": "🔢",
    "payment_question":     "💳",
    "unavailable_item":     "❌",
    "clarification":        "🔁",
    "other":                "❓",
}

# ---------- Language fallback ----------

LANG_FALLBACK = "zh"


def _classify_intent(text: str) -> str:
    lowered = text.lower()
    for intent, patterns in INTENT_RULES:
        for pattern in patterns:
            if re.search(pattern, lowered):
                return intent
    return "other"


def classify(text: str, user_language: str = "zh") -> ClassificationResponse:
    intent = _classify_intent(text)
    template = TEMPLATES[intent]
    lang = user_language if user_language in template else LANG_FALLBACK

    return ClassificationResponse(
        original_text=text,
        intent=intent,
        translated_text=template[lang],
        suggested_responses=template["suggested_responses"],
        visual_hint=template["visual_hint"],
    )
