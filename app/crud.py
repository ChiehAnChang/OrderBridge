import json
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session as DBSession
from app import models, schemas


# ---------- Session ----------

def create_session(db: DBSession, data: schemas.SessionCreate) -> models.Session:
    session = models.Session(
        user_language=data.user_language,
        restaurant_name=data.restaurant_name,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: DBSession, session_id: int) -> Optional[models.Session]:
    return db.query(models.Session).filter(models.Session.session_id == session_id).first()


def complete_session(db: DBSession, session_id: int) -> Optional[models.Session]:
    session = get_session(db, session_id)
    if not session:
        return None
    session.status = "completed"
    session.completed_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session


# ---------- ConversationTurn ----------

def add_turn(db: DBSession, data: schemas.ConversationTurnCreate) -> models.ConversationTurn:
    turn = models.ConversationTurn(
        session_id=data.session_id,
        speaker=data.speaker,
        original_text=data.original_text,
        translated_text=data.translated_text,
        intent=data.intent,
        suggested_responses=json.dumps(data.suggested_responses) if data.suggested_responses else None,
        selected_response=data.selected_response,
        final_response_text=data.final_response_text,
    )
    db.add(turn)
    db.commit()
    db.refresh(turn)
    return turn


def get_turns_by_session(db: DBSession, session_id: int) -> list[models.ConversationTurn]:
    return (
        db.query(models.ConversationTurn)
        .filter(models.ConversationTurn.session_id == session_id)
        .order_by(models.ConversationTurn.timestamp)
        .all()
    )


# ---------- Vocabulary ----------

def save_vocabulary(db: DBSession, data: schemas.VocabularySave) -> models.Vocabulary:
    vocab = models.Vocabulary(
        session_id=data.session_id,
        source=data.source,
        word=data.word,
        translation=data.translation,
        image_url=data.image_url,
        warning=data.warning,
    )
    db.add(vocab)
    db.commit()
    db.refresh(vocab)
    return vocab


def get_history_by_date(db: DBSession, date_str: str) -> list[models.Vocabulary]:
    from datetime import date
    try:
        target = date.fromisoformat(date_str)
    except ValueError:
        return []
    return (
        db.query(models.Vocabulary)
        .filter(models.Vocabulary.timestamp >= datetime(target.year, target.month, target.day, 0, 0, 0))
        .filter(models.Vocabulary.timestamp < datetime(target.year, target.month, target.day, 23, 59, 59))
        .order_by(models.Vocabulary.timestamp)
        .all()
    )


# ---------- Helper: deserialize suggested_responses ----------

def deserialize_turn(turn: models.ConversationTurn) -> schemas.ConversationTurnResponse:
    suggested = json.loads(turn.suggested_responses) if turn.suggested_responses else None
    return schemas.ConversationTurnResponse(
        turn_id=turn.turn_id,
        session_id=turn.session_id,
        timestamp=turn.timestamp,
        speaker=turn.speaker,
        original_text=turn.original_text,
        translated_text=turn.translated_text,
        intent=turn.intent,
        suggested_responses=suggested,
        selected_response=turn.selected_response,
        final_response_text=turn.final_response_text,
    )
