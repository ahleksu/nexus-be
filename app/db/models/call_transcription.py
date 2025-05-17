from typing import Optional
from datetime import datetime, timedelta
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship




class TranscriptionRole(str, Enum):
    AGENT = "agent"
    CUSTOMER = "customer"

class CallTranscription(SQLModel, table=True):
    call_transcription_id: Optional[int] = Field(default=None, primary_key=True)
    call_session_id: int = Field(foreign_key="call_sessions.call_session_id", index=True)

    timestamp: Optional[timedelta] = Field(default=None)
    transcription: str = Field(...)
    role: Optional[TranscriptionRole] = Field(default=None)
    call_file: Optional[str] = Field(default=None, max_length=500)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None, index=True)

    call_session: Optional["CallSession"] = Relationship(back_populates="transcriptions")

    def __repr__(self):
        return (
            f"<CallTranscription("
            f"id={self.call_transcription_id}, role={self.role}, "
            f"session={self.call_session_id})>"
        )

