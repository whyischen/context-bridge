"""
分块策略管理器实现
管理和演进分割算法
"""
import re
from typing import List, Dict, Any, Optional, Type, Callable
from core.interfaces.chunk_strategy_manager import IChunkStrategy, IChunkStrategyManager
from core.utils.logger import get_logger

logger = get_logger("chunk_strategy")


class BaseChunkStrategy(IChunkStrategy):
    """基础分块策略"""
    
    def __init__(self, name: str, version: str = "1.0.0"):
        self.name = name
        self.version = version
    
    def get_name(self) -> str:
        return self.name
    
    def get_version(self) -> str:
        return self.version
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__class__.__doc__ or "",
        }


class ParagraphChunkStrategy(BaseChunkStrategy):
    """按段落分割策略 - 按双换行符分割，保持段落完整性"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        super().__init__("paragraph", "1.0.0")
        self._validate_params(chunk_size, chunk_overlap)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @staticmethod
    def _validate_params(chunk_size: int, chunk_overlap: int) -> None:
        """验证参数合法性"""
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
    
    def split(self, text: str, **kwargs) -> List[str]:
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        
        # 验证运行时参数
        self._validate_params(chunk_size, chunk_overlap)
        
        if not text:
            return []
        
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            
            p_len = len(p)
            if current_length + p_len > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                overlap = current_chunk[-1] if current_chunk and len(current_chunk[-1]) <= chunk_overlap else ""
                current_chunk = [overlap, p] if overlap else [p]
                current_length = sum(len(x) for x in current_chunk) + (2 if overlap else 0)
            else:
                current_chunk.append(p)
                current_length += p_len + (2 if len(current_chunk) > 1 else 0)
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def get_metadata(self) -> Dict[str, Any]:
        meta = super().get_metadata()
        meta.update({
            "description": "按段落分割策略 - 按双换行符分割，保持段落完整性",
            "parameters": {
                "chunk_size": {"type": "int", "default": 800, "description": "每个chunk的目标字数"},
                "chunk_overlap": {"type": "int", "default": 150, "description": "chunks之间的重叠字数"}
            }
        })
        return meta


class CharacterChunkStrategy(BaseChunkStrategy):
    """按字符分割策略 - 严格按字数分割，尽量在空格处断开"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        super().__init__("character", "1.0.0")
        self._validate_params(chunk_size, chunk_overlap)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @staticmethod
    def _validate_params(chunk_size: int, chunk_overlap: int) -> None:
        """验证参数合法性"""
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
    
    def extract_l0_abstract(self, filename: str, content: str) -> str:
        """
        提取 L0 摘要 - 严格按字数控制
        
        Args:
            filename: 文件名
            content: 文档内容
            
        Returns:
            L0 摘要字符串
        """
        from core.i18n import t
        
        # 提取标题
        title_match = re.search(r'^\s*#+\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename
        
        # 严格按字数提取摘要（与 chunk_size 一致的逻辑）
        # 去除标题行
        content_without_title = re.sub(r'^\s*#+\s+.+$', '', content, count=1, flags=re.MULTILINE)
        
        # 提取前 200 个字符作为摘要
        summary = content_without_title.strip()[:200]
        if len(content_without_title.strip()) > 200:
            summary += "..."
        
        return f"{t('abstract_title')}: {title}\n{t('abstract_summary')}: {summary}"
    
    def split(self, text: str, **kwargs) -> List[str]:
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        
        # 验证运行时参数
        self._validate_params(chunk_size, chunk_overlap)
        
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            if end < len(text):
                last_space = text.rfind('\n', start, end)
                if last_space == -1:
                    last_space = text.rfind(' ', start, end)
                
                if last_space > start:
                    end = last_space + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - chunk_overlap if end < len(text) else end
        
        return chunks
    
    def get_metadata(self) -> Dict[str, Any]:
        meta = super().get_metadata()
        meta.update({
            "description": "按字符分割策略 - 严格按字数分割，尽量在空格处断开",
            "parameters": {
                "chunk_size": {"type": "int", "default": 800},
                "chunk_overlap": {"type": "int", "default": 150}
            }
        })
        return meta


class MarkdownHeaderChunkStrategy(BaseChunkStrategy):
    """按Markdown标题分割策略 - 语义感知，按标题级别分割"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150, max_header_level: int = 3):
        super().__init__("markdown_header", "1.0.0")
        self._validate_params(chunk_size, chunk_overlap, max_header_level)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_header_level = max_header_level
    
    @staticmethod
    def _validate_params(chunk_size: int, chunk_overlap: int, max_header_level: int) -> None:
        """验证参数合法性"""
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
        if not 1 <= max_header_level <= 6:
            raise ValueError(f"max_header_level must be between 1 and 6, got {max_header_level}")
    
    def extract_l1_outline(self, content: str) -> str:
        """
        提取 L1 大纲 - 与分割策略一致，只提取到 max_header_level
        
        Args:
            content: 文档内容
            
        Returns:
            L1 大纲字符串
        """
        # 提取到指定级别的标题
        pattern = r'^(#{1,' + str(self.max_header_level) + r'})\s+(.+)$'
        headers = re.findall(pattern, content, re.MULTILINE)
        
        if not headers:
            return "【文档大纲】: 无明确结构"
            
        outline = [f"【文档大纲】(H1-H{self.max_header_level}):"]
        for hashes, text in headers:
            indent = "  " * (len(hashes) - 1)
            outline.append(f"{indent}- {text.strip()}")
            
        full_outline = "\n".join(outline)
        if len(full_outline) > 1000:
            return full_outline[:997] + "..."
        return full_outline
    
    def split(self, text: str, **kwargs) -> List[str]:
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        max_header_level = kwargs.get("max_header_level", self.max_header_level)
        
        # 验证运行时参数
        self._validate_params(chunk_size, chunk_overlap, max_header_level)
        
        if not text:
            return []
        
        pattern = r'\n(?=' + '#' * max_header_level + r'\s)'
        sections = re.split(pattern, text)
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            section_len = len(section)
            
            if section_len > chunk_size:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                sub_chunks = self._split_large_section(section, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
            elif current_length + section_len > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                overlap = current_chunk[-1] if current_chunk and len(current_chunk[-1]) <= chunk_overlap else ""
                current_chunk = [overlap, section] if overlap else [section]
                current_length = sum(len(x) for x in current_chunk) + (2 if overlap else 0)
            else:
                current_chunk.append(section)
                current_length += section_len + (2 if len(current_chunk) > 1 else 0)
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def _split_large_section(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """对超大section按段落分割"""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
            
            p_len = len(p)
            if current_length + p_len > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                overlap = current_chunk[-1] if current_chunk and len(current_chunk[-1]) <= chunk_overlap else ""
                current_chunk = [overlap, p] if overlap else [p]
                current_length = sum(len(x) for x in current_chunk) + (2 if overlap else 0)
            else:
                current_chunk.append(p)
                current_length += p_len + (2 if len(current_chunk) > 1 else 0)
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def get_metadata(self) -> Dict[str, Any]:
        meta = super().get_metadata()
        meta.update({
            "description": "按Markdown标题分割策略 - 语义感知，按标题级别分割",
            "parameters": {
                "chunk_size": {"type": "int", "default": 800},
                "chunk_overlap": {"type": "int", "default": 150},
                "max_header_level": {"type": "int", "default": 3, "description": "最大标题级别(1-6)"}
            }
        })
        return meta


class RegexChunkStrategy(BaseChunkStrategy):
    """正则表达式分割策略 - 按自定义正则表达式分割"""
    
    def __init__(self, separator_pattern: str = r'\n(?=#{1,6}\s)', chunk_size: int = 800, chunk_overlap: int = 150):
        super().__init__("regex", "1.0.0")
        self._validate_params(chunk_size, chunk_overlap)
        self.separator_pattern = separator_pattern
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @staticmethod
    def _validate_params(chunk_size: int, chunk_overlap: int) -> None:
        """验证参数合法性"""
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
    
    def split(self, text: str, **kwargs) -> List[str]:
        separator_pattern = kwargs.get("separator_pattern", self.separator_pattern)
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        
        # 验证运行时参数
        self._validate_params(chunk_size, chunk_overlap)
        
        if not text:
            return []
        
        sections = re.split(separator_pattern, text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
            
            section_len = len(section)
            
            if section_len > chunk_size:
                if current_chunk:
                    chunks.append("\n\n".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                sub_chunks = self._split_large_section(section, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
            elif current_length + section_len > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                overlap = current_chunk[-1] if current_chunk and len(current_chunk[-1]) <= chunk_overlap else ""
                current_chunk = [overlap, section] if overlap else [section]
                current_length = sum(len(x) for x in current_chunk) + (2 if overlap else 0)
            else:
                current_chunk.append(section)
                current_length += section_len + (2 if len(current_chunk) > 1 else 0)
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def _split_large_section(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """对超大section进行字符级分割"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            if end < len(text):
                last_newline = text.rfind('\n', start, end)
                if last_newline > start:
                    end = last_newline + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - chunk_overlap if end < len(text) else end
        
        return chunks
    
    def get_metadata(self) -> Dict[str, Any]:
        meta = super().get_metadata()
        meta.update({
            "description": "正则表达式分割策略 - 按自定义正则表达式分割",
            "parameters": {
                "separator_pattern": {"type": "str", "default": r'\n(?=#{1,6}\s)', "description": "分割正则表达式"},
                "chunk_size": {"type": "int", "default": 800},
                "chunk_overlap": {"type": "int", "default": 150}
            }
        })
        return meta


class CustomChunkStrategy(BaseChunkStrategy):
    """自定义分割策略 - 使用自定义函数"""
    
    def __init__(self, split_func: Callable[[str], List[str]], name: str = "custom", version: str = "1.0.0"):
        super().__init__(name, version)
        self.split_func = split_func
    
    def split(self, text: str, **kwargs) -> List[str]:
        return self.split_func(text)
    
    def get_metadata(self) -> Dict[str, Any]:
        meta = super().get_metadata()
        meta.update({
            "description": "自定义分割策略",
            "custom": True
        })
        return meta


class SemanticChunkStrategy(BaseChunkStrategy):
    """语义分块策略 - 基于句子嵌入相似度的智能分割"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150, 
                 similarity_threshold: float = 0.5, use_percentile: bool = True,
                 percentile_threshold: int = 80):
        super().__init__("semantic", "1.0.0")
        self._validate_params(chunk_size, chunk_overlap, similarity_threshold, percentile_threshold)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.similarity_threshold = similarity_threshold
        self.use_percentile = use_percentile
        self.percentile_threshold = percentile_threshold
        self._embedding_model = None
    
    @staticmethod
    def _validate_params(chunk_size: int, chunk_overlap: int, 
                        similarity_threshold: float, percentile_threshold: int) -> None:
        """验证参数合法性"""
        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(f"chunk_overlap ({chunk_overlap}) must be less than chunk_size ({chunk_size})")
        if not 0 <= similarity_threshold <= 1:
            raise ValueError(f"similarity_threshold must be between 0 and 1, got {similarity_threshold}")
        if not 0 <= percentile_threshold <= 100:
            raise ValueError(f"percentile_threshold must be between 0 and 100, got {percentile_threshold}")
    
    def _get_embedding_model(self):
        """延迟加载嵌入模型"""
        if self._embedding_model is None:
            try:
                from core.embeddings.gte_small_zh import GTESmallZhONNX
                self._embedding_model = GTESmallZhONNX()
                logger.debug("Loaded GTE-Small-Zh embedding model for semantic chunking")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise RuntimeError(f"Cannot initialize semantic chunking without embedding model: {e}")
        return self._embedding_model
    
    def _split_sentences(self, text: str) -> List[str]:
        """将文本分割为句子"""
        # 支持中英文句子分割
        import re
        # 中文句号、英文句号、问号、感叹号后跟空白符
        pattern = r'(?<=[。！？.?!])\s+'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _combine_sentences(self, sentences: List[str]) -> List[str]:
        """为每个句子添加上下文窗口（前一句 + 当前句 + 后一句）"""
        combined = []
        for i in range(len(sentences)):
            parts = [sentences[i]]
            if i > 0:
                parts.insert(0, sentences[i-1])
            if i < len(sentences) - 1:
                parts.append(sentences[i+1])
            combined.append(' '.join(parts))
        return combined
    
    def _calculate_cosine_distances(self, embeddings: List[List[float]]) -> List[float]:
        """计算相邻句子嵌入的余弦距离"""
        import numpy as np
        distances = []
        for i in range(len(embeddings) - 1):
            vec1 = np.array(embeddings[i])
            vec2 = np.array(embeddings[i + 1])
            # 余弦相似度
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            # 余弦距离 = 1 - 相似度
            distance = 1 - similarity
            distances.append(distance)
        return distances
    
    def split(self, text: str, **kwargs) -> List[str]:
        chunk_size = kwargs.get("chunk_size", self.chunk_size)
        chunk_overlap = kwargs.get("chunk_overlap", self.chunk_overlap)
        similarity_threshold = kwargs.get("similarity_threshold", self.similarity_threshold)
        use_percentile = kwargs.get("use_percentile", self.use_percentile)
        percentile_threshold = kwargs.get("percentile_threshold", self.percentile_threshold)
        
        # 验证运行时参数
        self._validate_params(chunk_size, chunk_overlap, similarity_threshold, percentile_threshold)
        
        if not text:
            return []
        
        # 1. 分割句子
        sentences = self._split_sentences(text)
        if len(sentences) <= 1:
            return [text]
        
        # 2. 添加上下文窗口
        combined_sentences = self._combine_sentences(sentences)
        
        # 3. 生成嵌入
        model = self._get_embedding_model()
        embeddings = model.embed_batch(combined_sentences)
        
        # 4. 计算余弦距离
        distances = self._calculate_cosine_distances(embeddings)
        
        # 5. 确定分块边界
        if use_percentile:
            import numpy as np
            threshold = np.percentile(distances, percentile_threshold)
        else:
            threshold = similarity_threshold
        
        breakpoint_indices = [i for i, dist in enumerate(distances) if dist > threshold]
        
        # 6. 创建分块
        chunks = []
        start_idx = 0
        
        for bp_idx in breakpoint_indices:
            chunk_sentences = sentences[start_idx:bp_idx + 1]
            chunk_text = ' '.join(chunk_sentences)
            
            # 如果分块过大，进一步分割
            if len(chunk_text) > chunk_size:
                sub_chunks = self._split_large_chunk(chunk_text, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
            else:
                chunks.append(chunk_text)
            
            start_idx = bp_idx + 1
        
        # 添加最后一个分块
        if start_idx < len(sentences):
            chunk_text = ' '.join(sentences[start_idx:])
            if len(chunk_text) > chunk_size:
                sub_chunks = self._split_large_chunk(chunk_text, chunk_size, chunk_overlap)
                chunks.extend(sub_chunks)
            else:
                chunks.append(chunk_text)
        
        return [c for c in chunks if c.strip()]
    
    def _split_large_chunk(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """对超大分块按字符级别分割"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + chunk_size, len(text))
            
            # 尝试在空白符处断开
            if end < len(text):
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - chunk_overlap if end < len(text) else end
        
        return chunks
    
    def extract_l0_abstract(self, filename: str, content: str) -> str:
        """
        提取 L0 摘要 - 基于语义理解提取文档摘要
        
        Args:
            filename: 文件名
            content: 文档内容
            
        Returns:
            L0 摘要字符串
        """
        from core.i18n import t
        import re
        
        # 提取标题
        title_match = re.search(r'^\s*#+\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename
        
        # 去除标题行
        content_without_title = re.sub(r'^\s*#+\s+.+$', '', content, count=1, flags=re.MULTILINE)
        
        # 提取前几个句子作为摘要（更符合语义）
        sentences = self._split_sentences(content_without_title.strip())
        
        # 取前 2-3 个句子，但不超过 200 字符
        summary_sentences = []
        summary_length = 0
        for sentence in sentences[:3]:  # 最多取 3 个句子
            if summary_length + len(sentence) > 200:
                break
            summary_sentences.append(sentence)
            summary_length += len(sentence)
        
        summary = ' '.join(summary_sentences)
        if len(content_without_title.strip()) > summary_length:
            summary += "..."
        
        return f"{t('abstract_title')}: {title}\n{t('abstract_summary')}: {summary}"
    
    def extract_l1_outline(self, content: str) -> str:
        """
        提取 L1 大纲 - 基于语义分块提取文档结构
        
        Args:
            content: 文档内容
            
        Returns:
            L1 大纲字符串
        """
        import re
        
        # 首先尝试提取 Markdown 标题
        headers = re.findall(r'^(#{1,3})\s+(.+)$', content, re.MULTILINE)
        
        if headers:
            # 如果有 Markdown 标题，使用标题作为大纲
            outline = ["【文档大纲】(基于标题):"]
            for hashes, text in headers:
                indent = "  " * (len(hashes) - 1)
                outline.append(f"{indent}- {text.strip()}")
            
            full_outline = "\n".join(outline)
            if len(full_outline) > 1000:
                return full_outline[:997] + "..."
            return full_outline
        
        # 如果没有标题，使用语义分块的第一句作为大纲
        try:
            # 使用较高的阈值进行粗粒度分块
            chunks = self.split(content, percentile_threshold=90)
            
            if not chunks:
                return "【文档大纲】: 无明确结构"
            
            outline = ["【文档大纲】(基于语义分块):"]
            for i, chunk in enumerate(chunks[:10], 1):  # 最多显示 10 个分块
                # 提取每个分块的第一句作为概要
                sentences = self._split_sentences(chunk)
                if sentences:
                    first_sentence = sentences[0][:50]  # 限制长度
                    if len(sentences[0]) > 50:
                        first_sentence += "..."
                    outline.append(f"  {i}. {first_sentence}")
            
            full_outline = "\n".join(outline)
            if len(full_outline) > 1000:
                return full_outline[:997] + "..."
            return full_outline
            
        except Exception as e:
            logger.warning(f"Failed to extract L1 outline using semantic chunking: {e}")
            return "【文档大纲】: 提取失败"
    
    def get_metadata(self) -> Dict[str, Any]:
        meta = super().get_metadata()
        meta.update({
            "description": "语义分块策略 - 基于句子嵌入相似度的智能分割",
            "parameters": {
                "chunk_size": {"type": "int", "default": 800, "description": "每个chunk的目标字数"},
                "chunk_overlap": {"type": "int", "default": 150, "description": "chunks之间的重叠字数"},
                "similarity_threshold": {"type": "float", "default": 0.5, "description": "余弦距离阈值（0-1）"},
                "use_percentile": {"type": "bool", "default": True, "description": "是否使用百分位阈值"},
                "percentile_threshold": {"type": "int", "default": 80, "description": "百分位阈值（0-100）"}
            },
            "requires_embedding_model": True
        })
        return meta


class ChunkStrategyManager(IChunkStrategyManager):
    """分块策略管理器实现"""
    
    def __init__(self, default_strategy: str = "semantic"):
        self._strategy_instances: Dict[str, IChunkStrategy] = {}  # 已实例化的策略
        self._strategy_classes: Dict[str, Type[IChunkStrategy]] = {}  # 策略类（延迟实例化）
        self._default_strategy = default_strategy
        self._lock = threading.Lock()  # 实例级别的锁
        
        # 注册内置策略类
        self._register_builtin_strategies()
    
    def _register_builtin_strategies(self) -> None:
        """注册内置策略类（不立即实例化）"""
        self._strategy_classes["paragraph"] = ParagraphChunkStrategy
        self._strategy_classes["character"] = CharacterChunkStrategy
        self._strategy_classes["markdown_header"] = MarkdownHeaderChunkStrategy
        self._strategy_classes["regex"] = RegexChunkStrategy
        self._strategy_classes["semantic"] = SemanticChunkStrategy
        
        logger.debug(f"Registered {len(self._strategy_classes)} builtin chunk strategy classes")
    
    def get_strategy(self, strategy_name: str, **kwargs) -> IChunkStrategy:
        """
        获取策略实例（延迟实例化）
        
        Args:
            strategy_name: 策略名称
            **kwargs: 传递给策略构造函数的参数（如 chunk_size, chunk_overlap）
        
        Returns:
            IChunkStrategy 实例
        """
        # 如果没有传递参数，尝试返回已缓存的实例
        if not kwargs and strategy_name in self._strategy_instances:
            return self._strategy_instances[strategy_name]
        
        # 如果策略类存在，创建新实例
        if strategy_name in self._strategy_classes:
            strategy_class = self._strategy_classes[strategy_name]
            instance = strategy_class(**kwargs)
            
            # 如果没有自定义参数，缓存实例
            if not kwargs:
                with self._lock:
                    self._strategy_instances[strategy_name] = instance
            
            return instance
        
        # 检查是否有已注册的实例
        if strategy_name in self._strategy_instances:
            return self._strategy_instances[strategy_name]
        
        raise ValueError(
            f"Strategy '{strategy_name}' not found. "
            f"Available: {', '.join(self.list_strategies())}"
        )
    
    def register_strategy(self, name: str, strategy: IChunkStrategy) -> None:
        """注册策略实例"""
        with self._lock:
            self._strategy_instances[name] = strategy
        logger.debug(f"Registered chunk strategy instance: {name} (v{strategy.get_version()})")
    
    def register_strategy_class(self, name: str, strategy_class: Type[IChunkStrategy]) -> None:
        """注册策略类（延迟实例化）"""
        with self._lock:
            self._strategy_classes[name] = strategy_class
        logger.debug(f"Registered chunk strategy class: {name}")
    
    def list_strategies(self) -> List[str]:
        """列出所有可用策略"""
        all_strategies = set(self._strategy_instances.keys()) | set(self._strategy_classes.keys())
        return list(all_strategies)
    
    def get_default_strategy(self) -> str:
        """获取默认策略"""
        return self._default_strategy
    
    def set_default_strategy(self, strategy_name: str) -> None:
        """设置默认策略"""
        if strategy_name not in self.list_strategies():
            raise ValueError(f"Strategy '{strategy_name}' not found")
        self._default_strategy = strategy_name
        logger.debug(f"Set default chunk strategy to: {strategy_name}")
    
    def get_strategy_metadata(self, strategy_name: str) -> Dict[str, Any]:
        """获取策略元数据"""
        strategy = self.get_strategy(strategy_name)
        return strategy.get_metadata()


# 全局策略管理器实例（线程安全）
import threading

_global_strategy_manager: Optional[ChunkStrategyManager] = None
_manager_lock = threading.Lock()


def get_global_strategy_manager() -> ChunkStrategyManager:
    """获取全局策略管理器（线程安全）"""
    global _global_strategy_manager
    if _global_strategy_manager is None:
        with _manager_lock:
            # 双重检查锁定
            if _global_strategy_manager is None:
                _global_strategy_manager = ChunkStrategyManager()
    return _global_strategy_manager


def set_global_strategy_manager(manager: ChunkStrategyManager) -> None:
    """设置全局策略管理器（线程安全）"""
    global _global_strategy_manager
    with _manager_lock:
        _global_strategy_manager = manager
