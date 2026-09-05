import logging
import sys

from app.config.settings import settings


def setup_logging() -> None:
    """Uvicorn + app logging'i birlikte yapilandirir. api.py modul tepesinde cagrilir."""
    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(logger_name).setLevel(level)

    for logger_name in ["miralas.agent", "miralas.stt", "miralas.tts", "miralas.memory"]:
        logging.getLogger(logger_name).setLevel(level)