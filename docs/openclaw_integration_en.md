# OpenClaw Integration Guide (Skill Mode)

ContextBridge can be seamlessly integrated into OpenClaw as a native Skill. By providing a simple `SKILL.md` file, you can grant your OpenClaw agents the ability to read and search your local documents instantly.

## Architecture Design: Why SKILL.md?

OpenClaw is a powerful Multi-channel AI Gateway that uses a unique, prompt-based Skill system. Instead of writing complex Node.js or Python plugins, OpenClaw allows you to define a Skill using a simple Markdown file (`SKILL.md`).

1. **Zero-Code Integration**: You don't need to write any integration code. The `SKILL.md` file simply tells the AI *how* to use its existing tools (like `exec` or `bash`) to talk to ContextBridge.
2. **Native Compatibility**: This approach leverages OpenClaw's built-in tool execution capabilities, ensuring maximum compatibility and stability.
3. **Extreme Token Optimization**: The AI will never stuff an entire document into the Prompt. Through the API interface, it only retrieves the most relevant text chunks, greatly saving Tokens and improving answer accuracy.

---

## Step 1: Start ContextBridge API Service

Before connecting to OpenClaw, you need to have ContextBridge running in the background and providing the API service.

Open your terminal and run the following command:

```bash
# Start the API service (binds to 127.0.0.1:9790 by default)
cbridge serve
```

Once started, ContextBridge will do two things simultaneously:
1. Start the FastAPI server, listening on `http://127.0.0.1:9790`.
2. Start the Smart Folder Watcher in the background to monitor your local folder changes in real-time.

You can view the complete API documentation (Swagger UI) by visiting `http://127.0.0.1:9790/docs`.

---

## Step 2: Create the OpenClaw Skill

To integrate ContextBridge, you need to create a new Skill in your OpenClaw workspace.

1. Navigate to your OpenClaw skills directory (e.g., `~/.openclaw/skills/` or `<workspace>/skills/`).
2. Create a new folder named `contextbridge`.
3. Inside this folder, create a file named `SKILL.md` with the following content:

```markdown
---
name: contextbridge
description: Search and retrieve information from the user's local documents (Word, Excel, PDF, Markdown).
metadata: { "openclaw": { "emoji": "📚", "requires": { "bins": ["curl"] } } }
---

# ContextBridge Local Knowledge Base

You have access to the user's local documents via the ContextBridge API running at `http://127.0.0.1:9790`.

When the user asks about information that might be in their local files, you MUST use your `exec` or `bash` tool to query the ContextBridge API.

## How to Search Documents

To search for information, use `curl` to send a POST request to the `/api/v1/search` endpoint.

Example using `exec`:
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/search -H 'Content-Type: application/json' -d '{\"query\": \"marketing budget 2024\", \"top_k\": 3}'"
}
```

The API will return a JSON array of the most relevant text chunks, including the `content` and the `metadata.source` file path. Use this information to answer the user's question and cite the source file.

## How to Manage Watched Folders

If the user asks to add or remove a folder from the knowledge base, use the `/api/v1/watch/directories` endpoint.

To add a folder:
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/watch/directories -H 'Content-Type: application/json' -d '{\"path\": \"/absolute/path/to/folder\"}'"
}
```

To check which folders are currently being watched:
```json
{
  "command": "curl -s http://127.0.0.1:9790/api/v1/watch/status"
}
```
```

---

## Step 3: Enable the Skill in OpenClaw

Once the `SKILL.md` file is in place, you need to ensure the agent is allowed to use it.

1. Open your OpenClaw configuration (e.g., `~/.openclaw/openclaw.json` or your workspace config).
2. Ensure that `contextbridge` is added to the agent's `tools.allow` list, along with the required `exec` or `bash` tools (or `group:runtime`).

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "allow": [
            "group:runtime",
            "contextbridge"
          ]
        }
      }
    ]
  }
}
```

---

## Real Workflow Demonstration

Suppose a user asks in OpenClaw: **"According to the latest Q3 financial report, what is our marketing expenditure?"**

1. **Intent Recognition**: OpenClaw's LLM analyzes the question and reads the `contextbridge` Skill instructions.
2. **Tool Calling**: The LLM decides to use the `exec` tool to run the `curl` command against the ContextBridge API.
3. **API Response**: ContextBridge instantly returns the 3 most relevant text chunks, along with the source file `Q3_Report.pdf`.
4. **Final Generation**: The LLM synthesizes this data, generates a natural language answer for the user, and attaches the citation source.

If during the conversation, the user modifies the local `Q3_Report.pdf`, ContextBridge's background Watcher will instantly reconstruct the document's vectors. The next second the user asks again, the AI can immediately give an answer based on the latest modifications, entirely without manual intervention.

---

## Troubleshooting

* **API Connection Failed**: Please ensure `cbridge serve` is running and the port is not occupied (defaults to `9790`, will try other ports if occupied).
* **Cannot Search Latest Content**: Ask the AI to check the watch status to confirm if the target folder is in the watch list. If not, ask the AI to add it.
* **Curl Command Fails**: Ensure that `curl` is installed on the machine running OpenClaw (the Skill metadata specifies `"requires": { "bins": ["curl"] }`).
