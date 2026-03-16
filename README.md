# ContextBridge (cbridge-agent) 🌉

**The All-in-One Local Memory Bridge for AI Agents**

ContextBridge is a lightweight, zero-touch synchronization tool designed to connect your local files (Office documents, PDFs, TXT, Markdown) directly to AI Agents (like Claude Desktop) using the Model Context Protocol (MCP).

## 🚀 Why ContextBridge?

Unlike heavy enterprise solutions that require complex database setups, ContextBridge is designed for local, personal, and instant use:
- **Zero-Touch Sync**: Just drop a file into your watched folder, and it's instantly parsed, vectorized, and made available to your AI.
- **Batteries Included**: Built-in ChromaDB means no external database setup is required.
- **High-Fidelity Parsing**: Uses `markitdown` to perfectly extract text from Word, Excel, PPTX, PDF, and more.
- **MCP Ready**: Seamlessly integrates with Claude Desktop and other MCP-compatible AI clients.

## 📦 Installation

```bash
pip install cbridge-agent
```

## 🛠️ Quick Start

**1. Initialize your workspace:**
```bash
cbridge init
```

**2. Start the Bridge (Watch & MCP Server):**
```bash
cbridge start
```

## 🎯 Core Features

- **Multi-language Support**: Fully supports both English and Chinese interfaces. Switch easily with `cbridge lang en` or `cbridge lang zh`.
- **Watchdog Integration**: Real-time file system monitoring.
- **Auto-Vectorization**: Automatic chunking and embedding of your documents.
- **CLI Tooling**: Elegant and simple command-line interface.
