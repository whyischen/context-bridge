# OpenClaw Integration Guide

ContextBridge can be seamlessly integrated into OpenClaw as a Skill, enabling your AI agents to directly access and understand your local documents.

## What is ContextBridge Skill?

ContextBridge Skill is a powerful OpenClaw extension that provides:

- **Real-time Document Access** - Search and retrieve your local Word, Excel, PDF, and Markdown files instantly
- **Vector Search** - Intelligent semantic search across your document collection
- **Auto-Indexing** - Automatic parsing and indexing of new or modified documents
- **Zero Upload** - All documents stay on your machine, ensuring privacy and security

## Prerequisites

Before installing the ContextBridge Skill, ensure you have:

- OpenClaw installed and configured
- Python 3.8 or higher
- ContextBridge installed globally: `pip install cbridge-agent`

## Installation Steps

### Step 1: Install ContextBridge

```bash
pip install cbridge-agent
```

### Step 2: Initialize ContextBridge

Run the interactive setup:

```bash
cbridge init
```

This will guide you through:
- Choosing between embedded mode or external instance
- Configuring your document storage location
- Setting up the vector database

### Step 3: Add Folders to Monitor

Add the directories containing your documents:

```bash
cbridge watch add ~/Documents/MyProjects
cbridge watch add ~/Downloads/Research
```

You can add multiple folders as needed.

### Step 4: Build Initial Index

Create the initial vector index for your documents:

```bash
cbridge index
```

This will display a progress bar as it processes your documents.

### Step 5: Start ContextBridge

Launch the ContextBridge MCP server:

```bash
cbridge start
```

The server will run in the background and monitor your folders for changes.

### Step 6: Install ContextBridge Skill in OpenClaw

In OpenClaw:

1. Open the Skill marketplace
2. Search for "ContextBridge"
3. Click "Install"
4. Follow the configuration wizard

The Skill will automatically connect to your running ContextBridge instance.

## Using ContextBridge in OpenClaw

Once installed, you can use ContextBridge in your OpenClaw workflows:

### Search Documents

Ask your AI agent to search for information:

```
"Search my documents for information about project architecture"
```

The agent will:
1. Query ContextBridge for relevant documents
2. Retrieve matching content
3. Provide you with the results

### Read Specific Files

Request specific document content:

```
"Read the Q4 2024 financial report from my documents"
```

### Analyze Multiple Documents

Combine information from multiple sources:

```
"Compare the requirements from doc1.pdf and doc2.docx"
```

## Configuration

### Supported File Formats

- **Documents**: Word (.docx), Excel (.xlsx), PDF (.pdf)
- **Text**: Markdown (.md), Plain text (.txt)

### Folder Monitoring

Add or remove folders from monitoring:

```bash
# Add a folder
cbridge watch add /path/to/folder

# Remove a folder
cbridge watch remove /path/to/folder

# List monitored folders
cbridge watch list
```

### Search Settings

Customize search behavior in the Skill settings:

- **Max Results**: Number of documents to return (default: 5)
- **Similarity Threshold**: Minimum relevance score (default: 0.5)
- **Search Timeout**: Maximum search duration in seconds (default: 30)

## Troubleshooting

### Skill Not Connecting

**Problem**: OpenClaw can't connect to ContextBridge

**Solution**:
1. Verify ContextBridge is running: `cbridge status`
2. Check if the MCP server is listening on the correct port
3. Restart both ContextBridge and OpenClaw

### Documents Not Indexed

**Problem**: Your documents don't appear in search results

**Solution**:
1. Verify folders are being monitored: `cbridge watch list`
2. Check file formats are supported
3. Rebuild the index: `cbridge index --force`

### Slow Search Performance

**Problem**: Search queries are taking too long

**Solution**:
1. Reduce the number of monitored folders
2. Exclude large binary files
3. Increase the search timeout in Skill settings

### Memory Usage

**Problem**: ContextBridge is using too much memory

**Solution**:
1. Reduce the number of indexed documents
2. Clear old indexes: `cbridge clean`
3. Monitor folder size and archive old documents

## Advanced Configuration

### Custom Embedding Model

To use a different embedding model:

```bash
cbridge config set embedding_model "model-name"
```

Available models:
- `default` - Built-in model (recommended)
- `openai` - OpenAI embeddings (requires API key)
- `local` - Local model (requires additional setup)

### Batch Indexing

For large document collections:

```bash
cbridge index --batch-size 100 --workers 4
```

### Export and Backup

Backup your indexes:

```bash
cbridge export /path/to/backup
```

Restore from backup:

```bash
cbridge import /path/to/backup
```

## Performance Tips

1. **Organize Documents** - Use clear folder structures for better organization
2. **Regular Cleanup** - Archive old documents to keep indexes lean
3. **Batch Operations** - Index large collections during off-peak hours
4. **Monitor Resources** - Check memory and disk usage regularly

## FAQ

**Q: Can I use ContextBridge with multiple OpenClaw instances?**

A: Yes, you can run multiple ContextBridge instances on different ports and connect each OpenClaw instance to its own server.

**Q: Are my documents encrypted?**

A: Documents are stored locally on your machine. ContextBridge doesn't upload or transmit them. Encryption depends on your system's file system settings.

**Q: Can I update documents while ContextBridge is running?**

A: Yes, ContextBridge monitors folders in real-time and automatically indexes new or modified files.

**Q: What's the maximum number of documents I can index?**

A: There's no hard limit, but performance depends on your system resources. Most systems handle 10,000+ documents efficiently.

**Q: Can I use ContextBridge offline?**

A: Yes, ContextBridge works entirely offline. All processing happens locally on your machine.

## Getting Help

- **Documentation**: Check the [User Guide](./usage_en.md)
- **Issues**: Report bugs on [GitHub](https://github.com/whyischen/ContextBridge/issues)
- **Community**: Join our community discussions

## Next Steps

- Explore [advanced features](./usage_en.md#advanced-features)
- Learn about [best practices](./usage_en.md#best-practices)
- Check out [example workflows](./usage_en.md#example-workflows)
