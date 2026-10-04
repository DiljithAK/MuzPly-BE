import logging
from pathlib import Path


def configure_logging() -> logging.Logger:
    """Write application diagnostics to application.log in the project root."""
    logger = logging.getLogger("muzply")
    logger.setLevel(logging.INFO)

    if not any(
        getattr(handler, "_muzply_file_handler", False)
        for handler in logger.handlers
    ):
        log_path = Path(__file__).resolve().parents[2] / "application.log"
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler._muzply_file_handler = True  # type: ignore[attr-defined]
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)

    logger.propagate = False
    return logger
