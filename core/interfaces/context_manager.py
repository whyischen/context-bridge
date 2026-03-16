from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IContextManager(ABC):
    @abstractmethod
    def write_context(self, filename: str, content: str, level: str = "L2") -> bool:
        """
        写入上下文。
        例如：write_context("report.docx", "...", level="L2")
        """
        pass

    @abstractmethod
    def delete_context(self, filename: str) -> bool:
        """
        删除上下文。
        例如：delete_context("report.docx")
        """
        pass

    @abstractmethod
    def recursive_retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        执行高级检索策略（如 OpenViking 的目录递归检索）
        """
        pass

    @abstractmethod
    def get_all_filenames(self) -> List[str]:
        """
        获取所有已索引的文件名
        """
        pass
