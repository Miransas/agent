from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    status: str
    response: str
    session_id: str


class VoiceResponse(BaseModel):
    status: str
    transcript: str
    response: str
    session_id: str
