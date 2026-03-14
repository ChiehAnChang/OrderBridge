from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import crud, schemas
from app.database import get_db
from app.crud import deserialize_turn
from app.services.classifier import classify

router = APIRouter(tags=["Conversation"])


@router.post("/conversation/classify", response_model=schemas.ClassificationResponse)
def classify_text(data: schemas.ClassifyRequest):
    return classify(data.text, data.user_language)


@router.post("/turns/add", response_model=schemas.ConversationTurnResponse)
def add_turn(data: schemas.ConversationTurnCreate, db: DBSession = Depends(get_db)):
    session = crud.get_session(db, data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    turn = crud.add_turn(db, data)
    return deserialize_turn(turn)
