import logging
import logging.handlers
import sys
import re
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler

# Default log directory
DEFAULT_LOG_DIR = Path.home() / ".cbridge" / "logs"

def strip_rich_tags(text):
    """Remove Rich color tags, used for log file output."""
    if not isinstance(text, str):
        text = str(text)
    # Remove [xxx] and [/xxx] tags
    return re.sub(r'\[/?[a-zA-Z0-9_ ]+\]', '', text)

class RichTagStrippingFormatter(logging.Formatter):
    """Custom Formatter that removes Rich format tags before writing to file."""
    def format(self, record):
        # We format the entire log line and then strip tags
        message = super().format(record)
        return strip_rich_tags(message)

def setup_logger(name="cbridge", log_dir=None, level=logging.DEBUG):
    """
    Configure and return a global base Logger.
    Handles both console output (via Rich) and rotating file logs.
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if already configured
    if logger.handlers:
        if logger.level != level:
            logger.setLevel(level)
        return logger
        
    logger.setLevel(level)
    
    # 1. Determine log directory
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    else:
        log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 2. Format definitions
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 3. Console Handler (Only if in an interactive terminal to avoid redundancy in background logs)
    if sys.stderr.isatty():
        console_handler = RichHandler(
            console=Console(stderr=True),
            markup=True,
            show_time=False,   # Disable time in console
            show_level=False,  # Disable level in console
            show_path=False,
            rich_tracebacks=True
        )
        logger.addHandler(console_handler)
    
    # 4. Rotating File Handler (Always strips Rich tags)
    log_file = log_dir / f"{name}.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8"
    )
    file_handler.setFormatter(RichTagStrippingFormatter(log_format, date_format))
    
    # Compression functionality
    def namer(name):
        return name + ".gz"
    
    def rotator(source, dest):
        import gzip
        import shutil
        with open(source, "rb") as f_in:
            with gzip.open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        Path(source).unlink()
    
    file_handler.namer = namer
    file_handler.rotator = rotator
    
    logger.addHandler(file_handler)
    
    # 5. Suppress noisy third-party loggers
    noisy_loggers = [
        "docling", "docling.document_converter", "docling.models",
        "docling.utils", "docling.datamodel", "docling.pipeline",
        "rapidocr", "RapidOCR", "huggingface_hub", "transformers",
        "torch", "PIL", "chromadb", "uvicorn.access", "watchdog"
    ]
    for noisy_name in noisy_loggers:
        logging.getLogger(noisy_name).setLevel(logging.ERROR)
    
    return logger

def get_logger(name):
    """
    Get a sub-logger, child of the 'cbridge' main logger.
    Usage: logger = get_logger(__name__)
    """
    # Ensure root logger is initialized
    setup_logger("cbridge")
    
    # Use hierarchical naming: cbridge.core.watcher
    if name == "cbridge" or name.startswith("cbridge."):
        return logging.getLogger(name)
    
    return logging.getLogger(f"cbridge.{name}")
