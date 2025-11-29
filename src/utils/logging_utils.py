import logging
from pathlib import Path


def get_logger(name: str, level="INFO"):
    """
    Creates a consistent logger used across all agents.
    Logs both to console and logs/pipeline.log.
    """

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding handlers twice
    if not logger.handlers:
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        # File handler
        log_file = Path("logs/pipeline.log")
        log_file.parent.mkdir(exist_ok=True)

        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
