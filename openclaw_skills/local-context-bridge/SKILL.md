---
name: local-context-bridge
description: Search and retrieve information from the user's local documents, knowledge bases, policies, and historical data.
metadata: { "openclaw": { "emoji": "🌉", "requires": { "bins": ["curl"] } } }
---

# Local ContextBridge Knowledge Base

This skill allows OpenClaw to search and retrieve information from your local documents (PDF, Word, Excel, Markdown, etc.) using the ContextBridge API.

## 🛠️ PREREQUISITES & INSTALLATION

If you haven't installed the ContextBridge software on your machine yet, follow these steps first:

### 1. Install ContextBridge
Open your terminal and run:
```bash
pip install cbridge-agent
```

### 2. Initialize & Add Documents
Initialize your workspace and tell ContextBridge which folders to index:
```bash
cbridge init
cbridge watch add /path/to/your/documents
```

### 3. Start the API Service
ContextBridge must be running in the background to serve requests:
```bash
# Start both the file watcher and the API server
cbridge start
```
*The API server runs at `http://127.0.0.1:9790` by default.*

---

## 🧠 HOW IT WORKS (For New Users)

ContextBridge acts as a "Semantic Bridge" between your files and OpenClaw:

1.  **Local Indexing**: When you add a folder, ContextBridge scans your documents (PDF, Docx, etc.) and breaks them into small, manageable text chunks.
2.  **Vectorization**: Using a **local** AI embedding model, it converts these chunks into mathematical vectors that represent their *meaning*.
3.  **Semantic Search**: When OpenClaw asks a question, it doesn't just look for exact words. It uses the API to find the most *semantically relevant* chunks from your library.
4.  **100% Private**: All parsing, embedding, and searching happen **entirely on your local machine**. Your private data is never uploaded to any cloud service.

---

## WHEN TO USE THIS SKILL (Trigger Scenarios)

**DIRECTIVE**: If the user's request involves any information that is NOT general public knowledge, you MUST query ContextBridge before answering. Do NOT hallucinate or say "I don't have access" without trying a search first.

### 1. Deep Fact Retrieval (Private Knowledge)
Trigger this when the user asks for specific numbers, names, or facts buried in their local files.
- *Examples*: "What was the total budget for the 2024 marketing campaign?", "Who was the lead engineer for Project X?", "Find the summary of the meeting from last Friday."

### 2. Policy-Based Auditing & Compliance
Trigger this when you are asked to review, verify, or check a document. 
- **CRITICAL**: You must first search for local "policies", "guidelines", "SOPs", or "standards" to establish the ground truth before performing the audit.
- *Examples*: "Does this contract follow our standard procurement policy?", "Review this PR based on our internal coding standards."

### 3. Contextual Drafting (Style & Templates)
Trigger this when the user wants to write something that should match a previous style or use a specific local template.
- *Examples*: "Draft a project proposal using our standard company template", "Write a follow-up email in the same tone as my previous client communications."

### 4. Technical Support & Internal Processes
Trigger this for "How-to" questions regarding internal tools, deployment, or onboarding.
- *Examples*: "How do I set up the local development environment?", "What are the steps for the employee onboarding process?", "How do we handle database migrations?"

## SEARCH STRATEGY (Best Practices)

- **Extract Keywords**: Do NOT search using full conversational sentences. Extract core entities and keywords (e.g., search `"2024 marketing budget"` instead of `"What is the 2024 marketing budget?"`).
- **Iterative Searching**: If your first search returns empty or irrelevant results, try again using synonyms, broader terms, or different keywords.
- **Multiple Queries**: For complex tasks (like auditing), you may need to execute multiple `curl` commands to gather all necessary rules and context.

## HOW TO USE THE API

### 1. Search Documents
Send a POST request to `/api/v1/search` using `curl`.
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/search -H 'Content-Type: application/json' -d '{\"query\": \"2024 marketing budget\", \"top_k\": 3}'"
}
```
*The API returns a JSON array of text chunks. You MUST cite the `metadata.source` in your final answer (e.g., "According to `budget.xlsx`...").*

### 2. Manage Watched Folders
If the user asks to add or remove a folder to their knowledge base:
```json
{
  "command": "curl -s -X POST http://127.0.0.1:9790/api/v1/watch/directories -H 'Content-Type: application/json' -d '{\"path\": \"/absolute/path/to/folder\"}'"
}
```
To check currently watched folders:
```json
{
  "command": "curl -s http://127.0.0.1:9790/api/v1/watch/status"
}
```
