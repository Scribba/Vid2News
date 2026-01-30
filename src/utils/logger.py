import logging
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "newsfinder",
    level: int = logging.INFO,
    log_dir: str = "logs",
) -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    Path(log_dir).mkdir(exist_ok=True)
    log_file = Path(log_dir) / f"{name}_{datetime.now():%Y%m%d}.log"

    file = logging.FileHandler(log_file, encoding="utf-8")
    file.setFormatter(formatter)
    logger.addHandler(file)

    return logger

logger = setup_logger()