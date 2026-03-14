from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import crud, schemas
from app.database import get_db
from app.crud import deserialize_turn
from app.services import review as review_service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/create", response_model=schemas.SessionResponse)
def create_session(data: schemas.SessionCreate, db: DBSession = Depends(get_db)):
    return crud.create_session(db, data)


@router.post("/{session_id}/complete", response_model=schemas.SessionResponse)
def complete_session(session_id: int, db: DBSession = Depends(get_db)):
    session = crud.complete_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.get("/{session_id}/review", response_model=schemas.ReviewResponse)
def get_review(session_id: int, db: DBSession = Depends(get_db)):
    session = crud.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    raw_turns = crud.get_turns_by_session(db, session_id)
    turns = [deserialize_turn(t) for t in raw_turns]
    summary = review_service.generate_summary(turns)

    return schemas.ReviewResponse(
        session_info=schemas.SessionResponse.model_validate(session),
        turns=turns,
        learning_summary=summary,
    )
