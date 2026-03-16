from pathlib import Path
from typing import Set, Dict
from core.interfaces.parser import BaseParser

class CompositeParser(BaseParser):
    """
    A parser that delegates parsing to other parsers based on file extension.
    """
    
    def __init__(self, default_parser: BaseParser):
        self.default_parser = default_parser
        self.parsers: Dict[str, BaseParser] = {}
        self._all_extensions: Set[str] = set(default_parser.get_supported_extensions())

    def register_parser(self, parser: BaseParser, extensions: Set[str]):
        """Register a specific parser for a set of extensions."""
        for ext in extensions:
            self.parsers[ext.lower()] = parser
            self._all_extensions.add(ext.lower())

    def get_supported_extensions(self) -> Set[str]:
        return self._all_extensions

    def parse(self, file_path: Path, **kwargs) -> str:
        suffix = file_path.suffix.lower()
        parser = self.parsers.get(suffix, self.default_parser)
        return parser.parse(file_path, **kwargs)
