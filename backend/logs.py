from logging import DEBUG, FileHandler, Formatter, Logger, StreamHandler, getLogger as gl
from os import makedirs, path
from typing import Optional

from config import Logs as ConfigLog

_logger: Optional[Logger] = None
_logger_loaded: bool = False

def load_logger(
    logs: Optional[ConfigLog] = None,
    name: str = "app_logger",
    fmt: str = "[%(levelname)s] -> [%(asctime)s]: %(message)s",
    date_fmt: str = "%Y-%m-%d %H:%M",
    reload: bool = False,
) -> Logger:
    """Loads the logger using an explicit Logs config."""
    global _logger, _logger_loaded

    if _logger_loaded and not reload:
        return _logger

    logger = gl(name)
    logger.setLevel(logs.LOGS_LEVEL if logs else DEBUG)
    logger.handlers.clear()

    formatter = Formatter(
        logs.LOGS_FORMAT if logs and logs.LOGS_FORMAT else fmt,
        logs.LOGS_DATE_FORMAT if logs and logs.LOGS_DATE_FORMAT else date_fmt,
    )
    stream_handler = StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    disable_file = logs.LOGS_DISABLE if logs else False

    if not disable_file:
        log_dir = logs.LOGS_DIR if logs and logs.LOGS_DIR else "logs"
        log_file = logs.LOGS_FILE if logs and logs.LOGS_FILE else "app.log"
        log_path = path.join(log_dir, log_file)

        try:
            makedirs(log_dir, exist_ok=True)
            file_handler = FileHandler(log_path)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"No se pudo crear el file handler en '{log_path}': {e}")

    logger.propagate = False
    _logger = logger
    _logger_loaded = True
    return _logger

def get_logger(name: str = "app_logger") -> Logger:
    if not _logger_loaded:
        return load_logger(name=name)
    return _logger
