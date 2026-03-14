from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/history", tags=["History"])


@router.post("/save", response_model=schemas.VocabularyResponse)
def save_to_history(data: schemas.VocabularySave, db: DBSession = Depends(get_db)):
    session = crud.get_session(db, data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return crud.save_vocabulary(db, data)


@router.get("", response_model=schemas.HistoryResponse)
def get_history(date: str = str(date.today()), db: DBSession = Depends(get_db)):
    items = crud.get_history_by_date(db, date)
    return schemas.HistoryResponse(
        date=date,
        total_items=len(items),
        items=items,
    )
