#!/usr/bin/env python3
"""
Document Parser Wrapper for ContextBridge
"""

from pathlib import Path
import logging
import os
from typing import Optional

from core.parsers.markitdown_parser import MarkItDownParser
from core.parsers.docling_parser import DoclingParser
from core.parsers.composite_parser import CompositeParser
from core.interfaces.parser import BaseParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        
        # 3. Register specialized parsers
        try:
            docling_parser = DoclingParser()
            composite.register_parser(docling_parser, {'.pdf'})
            logger.info("Docling parser registered for PDF support")
        except ImportError:
            logger.warning("Docling not installed, falling back to MarkItDown for PDFs")
        except Exception as e:
            logger.error(f"Failed to initialize Docling: {e}")
            
        _current_parser = composite
    return _current_parser

def set_parser(parser: BaseParser):
    """Allow swapping the parser at runtime"""
    global _current_parser
    _current_parser = parser

def check_file_access(file_path: Path) -> tuple[bool, str]:
    """Check if file is accessible and within size limits"""
    if not file_path.exists():
        return False, f"File not found: {file_path}"
    
    if not file_path.is_file():
        return False, f"Not a file: {file_path}"
    
    if not os.access(file_path, os.R_OK):
        return False, f"No read permission: {file_path}"
    
    # Check file size (limit to 100MB)
    max_size = 100 * 1024 * 1024  # 100MB
    file_size = file_path.stat().st_size
    if file_size > max_size:
        return False, f"File too large ({file_size / 1024 / 1024:.1f}MB > {max_size / 1024 / 1024:.0f}MB limit)"
    
    return True, ""

def parse_document(file_path: Path, use_ocr: bool = True) -> str:
    """
    Parse document using the configured parser.
    Gracefully skips unsupported or inaccessible files.
    """
    # 1. Check file accessibility
    is_accessible, error_msg = check_file_access(file_path)
    if not is_accessible:
        logger.warning(f"Skipping file: {error_msg}")
        return ""
    
    # 2. Get the parser
    parser = get_parser()
    supported_exts = parser.get_supported_extensions()
    
    # 3. Check if extension is supported
    suffix = file_path.suffix.lower()
    if suffix not in supported_exts:
        # Silently skip or log a debug message for unsupported types
        # This fulfills the "skip unsupported files without affecting main flow" requirement
        logger.debug(f"Skipping unsupported file type: {suffix} ({file_path.name})")
        return ""
    
    # 4. Perform parsing
    try:
        content = parser.parse(file_path, use_ocr=use_ocr)
        if not content:
            logger.warning(f"Parser returned empty content for: {file_path.name}")
        return content
    except Exception as e:
        # Catch all exceptions to ensure main flow is not interrupted
        logger.error(f"Error parsing {file_path.name}: {e}")
        return ""

# For backward compatibility, we provide a property-like access
class _SupportedExtensionsProxy(set):
    def __contains__(self, item):
        return item in get_parser().get_supported_extensions()
    
    def __iter__(self):
        return iter(get_parser().get_supported_extensions())

SUPPORTED_EXTENSIONS = _SupportedExtensionsProxy()
