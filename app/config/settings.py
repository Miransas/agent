from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MIRALAS_",
        env_file=".env",
        extra="ignore",
    )

    # LLM (Ollama - OpenAI-compatible)
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: str = "ollama"
    llm_model: str = "llama3.1:8b"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 120

    # STT (faster-whisper)
    stt_model_size: str = "small"  # tiny | base | small | medium | large-v3
    stt_language: str = ""  # "" = otomatik; "tr" / "uz" sabitlenebilir

    # Server
    host: str = "127.0.0.1"
    port: int = 8000


settings = Settings()
