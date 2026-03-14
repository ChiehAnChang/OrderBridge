# OrderBridge

A restaurant ordering assistant for newcomers with limited English proficiency.
Users can take photos of menus, hear explanations, and respond by tapping buttons — without needing to read or write English.

---

## Project Overview

OrderBridge guides users through a full restaurant ordering interaction:

1. Scan a menu → understand dishes in their native language
2. Listen to the server → get an instant translation and response options
3. Tap to respond → no typing required
4. Review the conversation later → learn real English phrases from the interaction

**Target community:** Rohingya newcomers

---

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Backend  | FastAPI + SQLite + SQLAlchemy     |
| Frontend | Streamlit                         |
| Language | Python 3.9+                       |

---

## Repository Structure

```
app/
  config.py              # App settings and DB path
  database.py            # SQLAlchemy engine + session
  models.py              # ORM models: Session, ConversationTurn
  schemas.py             # Pydantic request/response schemas
  crud.py                # Database operations
  services/
    classifier.py        # Rule-based intent classification + translation templates
    review.py            # Learning summary generator
  routes/
    sessions.py          # Session management routes
    conversation.py      # Classification and turn routes
  main.py                # FastAPI entry point
frontend/
  review.py              # Streamlit review/learning page
requirements.txt
```

---

## Module Ownership

| Story | Description | Owner |
|-------|-------------|-------|
| Story 3 | Server speech understanding — classify what the server said, translate it, and provide tap-to-respond options | Jason |
| Story 5 | Conversation storage and review — save each interaction to SQLite, generate a learning summary for later review | Jason |

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the backend

```bash
uvicorn app.main:app --reload
```

The SQLite database (`orderbridge.db`) is created automatically on first run.
API docs available at: `http://localhost:8000/docs`

### 3. Start the review frontend

```bash
streamlit run frontend/review.py
```

Opens at: `http://localhost:8501`

---

## API Endpoints

### Sessions

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/sessions/create` | Start a new ordering session |
| POST | `/sessions/{id}/complete` | Mark a session as completed |
| GET | `/sessions/{id}/review` | Get full review with learning summary |

### Conversation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/conversation/classify` | Classify server speech + return translation and response options |
| POST | `/turns/add` | Save a conversation turn to the database |

---

## Example: Classify Server Speech

**Request:**
```json
POST /conversation/classify
{
  "text": "What size would you like?",
  "user_language": "roh"
}
```

**Response:**
```json
{
  "original_text": "What size would you like?",
  "intent": "size_choice",
  "translated_text": "...",
  "suggested_responses": ["Small", "Medium", "Large"],
  "visual_hint": "size_options"
}
```

---

## Supported Intents

| Intent | Trigger phrases |
|--------|----------------|
| `size_choice` | size, small, medium, large |
| `drink_choice` | drink, beverage, juice, soda, water, coffee |
| `combo_choice` | combo, meal deal, with fries |
| `dine_in_takeout` | for here, to go, take out, dine in |
| `spice_level` | spicy, mild, hot, no spice |
| `quantity_confirmation` | how many, quantity |
| `payment_question` | pay, cash, card, tap, Apple Pay |
| `unavailable_item` | out of stock, not available |
| `clarification` | pardon, repeat, didn't hear |
| `other` | fallback for anything else |

---

## Extending This Module

- **Add real speech-to-text:** Pass audio to `/conversation/classify` after transcribing with Whisper or similar. The classifier is decoupled from the input source.
- **Replace rule-based classifier with LLM:** Swap out `services/classifier.py` — the route and schema stay the same.
- **Add more languages:** Add a new language key to each intent template in `classifier.py`.
