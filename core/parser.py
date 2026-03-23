#!/usr/bin/env python3
"""
Document Parser Wrapper for ContextBridge
"""

from pathlib import Path
import os
from typing import Optional

from core.parsers.markitdown_parser import MarkItDownParser
from core.parsers.pdf_parser import PDFParser
from core.parsers.composite_parser import CompositeParser
from core.interfaces.parser import BaseParser
from core.config import CONFIG
from core.utils.logger import get_logger

logger = get_logger("parser")

# Global parser instance
_current_parser: Optional[BaseParser] = None

def get_parser() -> BaseParser:
    """Get the configured parser instance (singleton)"""
    global _current_parser
    if _current_parser is None:
        # 1. Initialize base parsers
        mid_parser = MarkItDownParser()

        # 2. Create composite router
        composite = CompositeParser(default_parser=mid_parser)

        # 3. Register specialized parsers based on config
        pdf_strategy = CONFIG.get("pdf_parser_strategy", "markitdown")
        logger.info(f"Using PDF parser strategy: {pdf_strategy}")

        try:
            pdf_parser = PDFParser(strategy=pdf_strategy)
            composite.register_parser(pdf_parser, {'.pdf'})
        except ImportError as e:
            logger.error(f"Failed to initialize PDF parser: {e}")
            logger.error("Please install required dependencies: pip install -r requirements.txt")

        _current_parser = composite
    return _current_parser

def set_parser(parser: BaseParser):
    """Allow swapping the parser at runtime"""
    global _current_parser
    _current_parser = parser

def check_file_access(file_path: Path) -> tuple[bool, str]:
    """Check if file is accessible and within size limits"""
    from core.config import CONFIG
    
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    if not file_path.is_file():
        return False, f"Not a file: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return False, f"No read permission: {file_path}"
    
    # Check file size (use config value, default 50MB)
    watcher_config = CONFIG.get("watcher", {})
    max_file_size_mb = watcher_config.get("max_file_size_mb", 50)
    max_size = max_file_size_mb * 1024 * 1024
    file_size = file_path.stat().st_size
    if file_size > max_size:
        return False, f"File too large ({file_size / 1024 / 1024:.1f}MB > {max_file_size_mb}MB limit)"
    
    return True, ""

def parse_document(file_path: Path, use_ocr: bool = True) -> tuple[str, str]:
    """
    Parse document using the configured parser.
    Returns (content, error_reason). error_reason is empty string on success.
    """
    # 1. Check file accessibility
    is_accessible, error_msg = check_file_access(file_path)
    if not is_accessible:
        return "", error_msg
    
    # 2. Get the parser
    parser = get_parser()
    supported_exts = parser.get_supported_extensions()
    
    # 3. Check if extension is supported
    suffix = file_path.suffix.lower()
    if suffix not in supported_exts:
        return "", f"Unsupported file type: {suffix}"
    
    # 4. Perform parsing
    try:
        content = parser.parse(file_path, use_ocr=use_ocr)
        if not content:
            return "", "Parser returned empty content"
        return content, ""
    except Exception as e:
        return "", str(e)

# For backward compatibility, we provide a property-like access
class _SupportedExtensionsProxy(set):
    def __contains__(self, item):
        return item in get_parser().get_supported_extensions()
    
    def __iter__(self):
        return iter(get_parser().get_supported_extensions())

SUPPORTED_EXTENSIONS = _SupportedExtensionsProxy()
