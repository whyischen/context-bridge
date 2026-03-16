from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Set

class BaseParser(ABC):
    """Abstract base class for document parsers."""
    
    @abstractmethod
    def parse(self, file_path: Path, **kwargs) -> str:
        """Parse a file and return its content as markdown string."""
        pass

    @abstractmethod
    def get_supported_extensions(self) -> Set[str]:
        """Return a set of supported file extensions (including the dot)."""
        pass
