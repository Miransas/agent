import logging

from fastapi import FastAPI, HTTPException

from app.core.types import ChatRequest, ChatResponse
from app.llm import client as llm_client
from app.llm.prompts import VOICE_SYSTEM_PROMPT

log = logging.getLogger("miralas.agent")

app = FastAPI(title="Miransas Voice Agent Core", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def generate_voice_response(request: ChatRequest) -> ChatResponse:
    try:
        text = await llm_client.generate(
            user_message=request.prompt,
            system_prompt=VOICE_SYSTEM_PROMPT,
        )
        return ChatResponse(status="success", response=text)
    except Exception as exc:
        log.exception("LLM call failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc
