from datetime import datetime
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_language: Mapped[str] = mapped_column(String(10), nullable=False, default="zh")
    restaurant_name: Mapped[str] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | completed
    order_summary: Mapped[str] = mapped_column(Text, nullable=True)

    turns: Mapped[list["ConversationTurn"]] = relationship(
        "ConversationTurn", back_populates="session", order_by="ConversationTurn.timestamp"
    )


class ConversationTurn(Base):
    __tablename__ = "conversation_turns"

    turn_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("sessions.session_id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    speaker: Mapped[str] = mapped_column(String(20), nullable=False)  # server | user | system
    original_text: Mapped[str] = mapped_column(Text, nullable=False)
    translated_text: Mapped[str] = mapped_column(Text, nullable=True)
    intent: Mapped[str] = mapped_column(String(50), nullable=True)
    suggested_responses: Mapped[str] = mapped_column(Text, nullable=True)  # JSON string
    selected_response: Mapped[str] = mapped_column(Text, nullable=True)
    final_response_text: Mapped[str] = mapped_column(Text, nullable=True)

    session: Mapped["Session"] = relationship("Session", back_populates="turns")
