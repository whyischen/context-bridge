from pathlib import Path
from typing import Set
import logging
from docling.document_converter import DocumentConverter
from core.interfaces.parser import BaseParser

logger = logging.getLogger(__name__)

class DoclingParser(BaseParser):
    """
    High-fidelity PDF parser using IBM's Docling.
    Best for complex layouts and tables.
    """
    
    def __init__(self):
        # Docling initialization can be heavy, so we do it on demand or once
        self._converter = DocumentConverter()
        self._supported_extensions = {'.pdf'}

    def get_supported_extensions(self) -> Set[str]:
        return self._supported_extensions

    def parse(self, file_path: Path, **kwargs) -> str:
        """Parse PDF using Docling and export to Markdown."""
        try:
            logger.info(f"Docling parsing PDF: {file_path.name}")
            result = self._converter.convert(str(file_path))
            
            # Export to markdown format which is best for AI agents
            markdown_content = result.document.export_to_markdown()
            return markdown_content or ""
            
        except Exception as e:
            logger.error(f"Docling failed to parse {file_path}: {e}")
            return ""
