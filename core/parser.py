from markitdown import MarkItDown
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_document(file_path: Path) -> str:
    logger.info(f"Parsing document: {file_path}")
    md = MarkItDown()
    try:
        result = md.convert(str(file_path))
        return result.text_content
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        return ""
