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
    stt_model_size: str = "tiny"
    stt_language: str = ""

    # Memory
    memory_max_messages: int = 20  # context penceresi (8b icin guvenli)
    memory_ttl_seconds: int = 3600  # 1 saat sonra oturum unutulur

    # Guvenlik / kaynak limitleri
    max_upload_bytes: int = 15 * 1024 * 1024  # ses dosyasi ust siniri (~15MB)
    audio_retention_seconds: int = 3600  # static/audio'daki eski dosyalar bu sureden sonra silinir

    # Logging
    log_level: str = "INFO"  # .env'den MIRALAS_LOG_LEVEL=DEBUG ile degistir

    # Server
    host: str = "127.0.0.1"
    port: int = 8000


settings = Settings()