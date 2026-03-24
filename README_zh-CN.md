[**🇨🇳 中文**](README_zh-CN.md) | [**🇬🇧 English**](README.md)

# ContextBridge (cbridge-agent)

> **让 AI 智能体 轻松读懂你的本地文档**
> 
> 专为 Openclaw、Cursor 等智能体设计的知识库插件。让你的 AI 助手轻松读取、理解本地的 Word、Excel 和 PDF 文件，无需上传，隐私安全。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/cbridge-agent.svg)](https://badge.fury.io/py/cbridge-agent)

🌐 **官方网站**: [https://contextbridge.chat](https://contextbridge.chat)

## OpenClaw Skill

ContextBridge 的原生 skill [local-context-bridge](https://clawhub.ai/whyischen/local-context-bridge-cn) 已发布至[clawhub.ai](https://clawhub.ai/)。

- [`openclaw_skills/local-context-bridge-cn`](openclaw_skills/local-context-bridge-cn/) - 中文环境
- [`openclaw_skills/local-context-bridge`](openclaw_skills/local-context-bridge/) - 英文环境

安装后 OpenClaw 自动识别，无需额外配置即可检索你的本地文档。

## 快速开始

### 安装

```bash
pip install cbridge-agent
```

首次运行会自动下载向量模型。

### 初始化

```bash
cbridge init
```

按向导完成配置（默认工作区在 `~/.cbridge`）。

### 添加文档目录

```bash
cbridge watch add /path/to/your/documents
```
目录中的文件变更会自动同步到向量数据库。

### 搜索文档内容

```bash
cbridge search ContextBridge
```

## 核心特性：智能文本分块

ContextBridge 采用三层递进式检索架构，确保 AI 能够精准定位文档内容：

### L0 层：文档摘要
自动提取文档标题和首段核心内容，快速判断文档相关性。

### L1 层：结构大纲
解析文档的标题层级（H1-H3），构建完整的内容导航地图。

### L2 层：语义分块
- 默认分块大小：800 字符
- 智能重叠：150 字符（保持上下文连贯性）
- 段落感知：按自然段落边界切分，避免语义割裂
- Markdown 友好：识别代码块、列表等结构，保持格式完整性

### 检索流程

1. **意图宽筛**：在 L0/L1 层快速匹配相关文档
2. **细粒度打捞**：在匹配文档的 L2 层精确检索相关片段
3. **上下文组装**：返回文档摘要 + 相关片段，提供完整语境

这种设计让 AI 既能快速定位目标文档，又能获取精确的上下文信息，避免传统 RAG 系统"只见树木不见森林"的问题。

## 其他 AI 客户端

除 OpenClaw 外，也支持 Claude Desktop、Cursor 等支持 MCP 的客户端：

```json
{
  "mcpServers": {
    "context-bridge": {
      "command": "cbridge",
      "args": ["mcp"]
    }
  }
}
```

## CLI 命令

| 命令 | 功能 |
|------|------|
| `cbridge init` | 交互式初始化配置(服务会默认启动，不需要手动执行 cbridge start) |
| `cbridge watch add <dir>` | 添加监控目录 |
| `cbridge watch list` | 列出监控目录 |
| `cbridge watch remove <dir>` | 移除监控目录 |
| `cbridge start` | 启动监控服务 |
| `cbridge serve` | 启动 API 服务与监控服务 |
| `cbridge index` | 全量重建索引 |
| `cbridge search "query"` | 测试语义搜索 |
| `cbridge status` | 查看运行状态 |
| `cbridge lang <zh\|en>` | 切换语言 |
| `cbridge logs -f` | 查看日志 |

## 常见问题

**Q: 如何切换 PDF 解析策略？**  
A: 编辑配置文件 `~/.cbridge/config.yaml`，将 `parser.pdf.strategy` 设为 `docling`（高精度但较慢）或 `markitdown`（轻量级默认）。

**Q: 支持哪些文件格式？**  
A: PDF、DOCX、XLSX、PPTX、MD、TXT 等。通过 MarkItDown 覆盖绝大多数办公文档。

**Q: 索引数据存储在哪里？**  
A: 所有数据保存在 `~/.cbridge/` 目录下，包括向量数据库和配置。

## 参与贡献

欢迎提交 Issue 和 Pull Request。

## 许可证

[MIT License](LICENSE)