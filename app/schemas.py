from datetime import datetime
from typing import Optional
from pydantic import BaseModel


# ---------- Session ----------

class SessionCreate(BaseModel):
    user_language: str = "zh"
    restaurant_name: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: int
    user_language: str
    restaurant_name: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    status: str
    order_summary: Optional[str]

    model_config = {"from_attributes": True}


# ---------- ConversationTurn ----------

class ConversationTurnCreate(BaseModel):
    session_id: int
    speaker: str                          # server | user | system
    original_text: str
    translated_text: Optional[str] = None
    intent: Optional[str] = None
    suggested_responses: Optional[list[str]] = None
    selected_response: Optional[str] = None
    final_response_text: Optional[str] = None


class ConversationTurnResponse(BaseModel):
    turn_id: int
    session_id: int
    timestamp: datetime
    speaker: str
    original_text: str
    translated_text: Optional[str]
    intent: Optional[str]
    suggested_responses: Optional[list[str]]
    selected_response: Optional[str]
    final_response_text: Optional[str]

    model_config = {"from_attributes": True}


# ---------- Vocabulary / History ----------

class VocabularySave(BaseModel):
    session_id: int
    source: str                          # ocr | speech
    word: str
    translation: Optional[str] = None
    image_url: Optional[str] = None
    warning: Optional[str] = None        # "pork" | None


class VocabularyResponse(BaseModel):
    vocab_id: int
    session_id: int
    timestamp: datetime
    source: str
    word: str
    translation: Optional[str]
    image_url: Optional[str]
    warning: Optional[str]

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    date: str
    total_items: int
    items: list[VocabularyResponse]


# ---------- Classifier ----------

class ClassifyRequest(BaseModel):
    text: str
    user_language: str = "zh"


class ClassificationResponse(BaseModel):
    original_text: str
    intent: str
    translated_text: str
    suggested_responses: list[str]
    visual_hint: str


# ---------- Review ----------

class KeyExpression(BaseModel):
    original: str
    translation: str
    intent: str
    suggested_responses: list[str]


class LearningSummary(BaseModel):
    total_turns: int
    server_turns: int
    key_expressions: list[KeyExpression]


class ReviewResponse(BaseModel):
    session_info: SessionResponse
    turns: list[ConversationTurnResponse]
    learning_summary: LearningSummary
