from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from prompt import VOICE_SYSTEM_PROMPT

app = FastAPI(title="Miransas Voice Agent Core")

OLLAMA_URL = "http://localhost:11434/api/generate"

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/chat")
async def generate_voice_response(request: ChatRequest):
    try:
        full_prompt = f"{VOICE_SYSTEM_PROMPT}\n\nKullanıcı: {request.prompt}\nAjan:"

        payload = {
            "model": "llama3.1:8b",
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 120 # Sesli yanıtların kısa kalması için token sınırı
            }
        }

        response = requests.post(OLLAMA_URL, json=payload)
        res_data = response.json()

        return {
            "status": "success",
            "response": res_data.get("response", "").strip()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)