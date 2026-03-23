import re
from typing import List, Dict
from core.i18n import t

class MarkdownTextSplitter:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        if not text:
            return []
            
        # 按可能具有语义的段落分隔符切分
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = []
        current_length = 0

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue
                
            p_len = len(p)
            # 如果加上当前段落超出了 chunk_size，且当前 chunk 不为空，就把当前 chunk 存起来
            if current_length + p_len > self.chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                # 实现简单的 overlap：尝试保留最后一个段落作为重叠内容（只要它不是太长）
                overlap = current_chunk[-1] if current_chunk and len(current_chunk[-1]) <= self.chunk_overlap else ""
                current_chunk = [overlap, p] if overlap else [p]
                current_length = sum(len(x) for x in current_chunk) + (2 if overlap else 0)
            else:
                current_chunk.append(p)
                current_length += p_len + (2 if len(current_chunk) > 1 else 0)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
            
        return chunks

class HeuristicExtractor:
    @staticmethod
    def extract_l0_abstract(filename: str, content: str) -> str:
        """
        利用启发式规则提取文档的 L0 结构化摘要
        """
        # 提取第一个 H1 或是 H2 作为真实标题
        title_match = re.search(r'^\s*#+\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename
        
        # 提取第一个有效正文段落（过滤掉标题、代码块、列表等格式文字）
        lines = content.split('\n')
        first_p = ""
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
                
            if in_code_block or not stripped:
                continue
                
            # 过滤掉标题、列表、引用或图片、链接的格式开头
            if re.match(r'^([#*>+\-]|!\[|\[)', stripped):
                continue
                
            # 找到一个大于 50 个字符的段落（通常才是人话）
            if len(stripped) > 50:
                first_p = stripped
                break
                
        # 兜底：如果没有长段落，就取第一行不是格式的非空文本
        if not first_p:
            for line in lines:
                if line.strip() and not re.match(r'^([#*>+\-```])', line.strip()):
                    first_p = line.strip()
                    break
                    
        # 防止摘要过度冗长
        if len(first_p) > 200:
            first_p = first_p[:197] + "..."
            
        return f"{t('abstract_title')}: {title}\n{t('abstract_summary')}: {first_p}"

    @staticmethod
    def extract_l1_outline(content: str) -> str:
        """
        利用正则提取文档所有大纲标题，生成 L1 总览
        """
        # 提取从 H1 到 H3 的标题
        headers = re.findall(r'^(#{1,3})\s+(.+)$', content, re.MULTILINE)
        if not headers:
            return "【文档大纲】: 无明确结构"
            
        outline = ["【文档大纲】:"]
        for hashes, text in headers:
            indent = "  " * (len(hashes) - 1)
            outline.append(f"{indent}- {text.strip()}")
            
        full_outline = "\n".join(outline)
        if len(full_outline) > 1000:
            return full_outline[:997] + "..."
        return full_outline
