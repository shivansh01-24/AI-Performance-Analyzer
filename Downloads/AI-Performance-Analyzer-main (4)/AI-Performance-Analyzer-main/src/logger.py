import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"


def get_logger(name: str = "ai_performance_analyzer") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        # Already configured
        return logger

    logger.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # File handler with rotation
    fh = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3)
    fh.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
