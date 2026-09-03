import logging
import sys


def setup_logging():
    """Uvicorn + app logging'i birlikte yapılandır."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Uvicorn loglarını da INFO seviyesine çek
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        logging.getLogger(logger_name).setLevel(logging.INFO)

    # App logları
    logging.getLogger("miralas.agent").setLevel(logging.INFO)
    logging.getLogger("miralas.stt").setLevel(logging.INFO)
    logging.getLogger("miralas.tts").setLevel(logging.INFO)


setup_logging()
