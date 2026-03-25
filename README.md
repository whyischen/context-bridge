![Banner](public/banner.png)

[**🇨🇳 中文**](README_zh-CN.md) | [**🇬🇧 English**](README.md)

# ContextBridge (cbridge-agent)

> **Connect AI Agents to your Local Documents**
>
> Local knowledge base for OpenClaw, Cursor and AI assistants. Read your documents instantly—Word, Excel, PDF. No uploads. Privacy first.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/cbridge-agent.svg)](https://badge.fury.io/py/cbridge-agent)

🌐 **Official Website**: [https://contextbridge.chat](https://contextbridge.chat)

## OpenClaw Skill

Native skills for ContextBridge [local-context-bridge](https://clawhub.ai/whyischen/local-context-bridge)  are available on [clawhub.ai](https://clawhub.ai/).

```bash
clawhub install local-context-bridge
```

Once installed, OpenClaw will automatically detect ContextBridge — no additional configuration needed to search your local documents.

## Quick Start

### Installation

```bash
pip install cbridge-agent
```

The vector model will be downloaded automatically on the first run.

### Initialization

```bash
cbridge init
```

Follow the interactive wizard to complete the configuration (the default workspace is at `~/.cbridge`).

### Add a Document Directory

```bash
cbridge watch add /path/to/your/documents
```

File changes in this directory will be automatically synced to the vector database.

### Search Document Content

```bash
cbridge search ContextBridge
```

## Core Feature: Intelligent Text Chunking

ContextBridge uses a three-tier progressive retrieval architecture to ensure AI can precisely locate document content:

### L0 Layer: Document Abstract

Automatically extracts document title and first paragraph core content for quick relevance assessment.

### L1 Layer: Structural Outline

Parses document heading hierarchy (H1-H3) to build a complete content navigation map.

### L2 Layer: Semantic Chunking

- Default chunk size: 800 characters
- Smart overlap: 150 characters (maintains context continuity)
- Paragraph-aware: Splits at natural paragraph boundaries to avoid semantic fragmentation
- Markdown-friendly: Recognizes code blocks, lists, and other structures to preserve formatting integrity

### Retrieval Process

1. **Intent Filtering**: Quickly match relevant documents at L0/L1 layers
2. **Fine-grained Retrieval**: Precisely search relevant fragments in L2 layer of matched documents
3. **Context Assembly**: Return document abstract + relevant excerpts to provide complete context

This design allows AI to quickly locate target documents while obtaining precise contextual information, avoiding the "can't see the forest for the trees" problem of traditional RAG systems.

## Other AI Clients

In addition to OpenClaw, ContextBridge also works with Claude Desktop, Cursor, and other MCP-compatible clients:

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

## CLI Commands

| Command                        | Description                                                                                              |
| ------------------------------ | -------------------------------------------------------------------------------------------------------- |
| `cbridge init`               | Interactive initialization (the service starts automatically; no need to run `cbridge start` manually) |
| `cbridge watch add <dir>`    | Add a directory to watch                                                                                 |
| `cbridge watch list`         | List watched directories                                                                                 |
| `cbridge watch remove <dir>` | Remove a watched directory                                                                               |
| `cbridge start`              | Start the watcher service                                                                                |
| `cbridge serve`              | Start both the API and watcher services                                                                  |
| `cbridge index`              | Rebuild the index from scratch                                                                           |
| `cbridge search "query"`     | Test semantic search                                                                                     |
| `cbridge status`             | Check running status                                                                                     |
| `cbridge lang <zh\|en>`       | Switch language                                                                                          |
| `cbridge logs -f`            | View logs                                                                                                |

## FAQ

**Q: How do I switch the PDF parsing strategy?**
A: Edit the configuration file at `~/.cbridge/config.yaml`, and set `parser.pdf.strategy` to `docling` (higher accuracy but slower) or `markitdown` (lightweight default).

**Q: What file formats are supported?**
A: PDF, DOCX, XLSX, PPTX, MD, TXT, and more. MarkItDown covers the vast majority of office document formats.

**Q: Where is the indexed data stored?**
A: All data is stored locally in the `~/.cbridge/` directory, including the vector database and configuration files.

## Contributing

Issues and Pull Requests are welcome.

## License

[MIT License](LICENSE)
