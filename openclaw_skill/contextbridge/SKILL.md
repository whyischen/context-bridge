---
name: contextbridge
description: Search and retrieve information from the user's local documents, knowledge bases, policies, and historical data.
metadata: { "openclaw": { "emoji": "📚", "requires": { "bins": ["curl"] } } }
---

# ContextBridge Local Knowledge Base

You are equipped with ContextBridge, a powerful local search engine running at `http://127.0.0.1:9790`. It grants you access to the user's private documents (Word, Excel, PDF, Markdown, etc.).

## WHEN TO USE THIS SKILL (Trigger Scenarios)

You MUST use your `exec` or `bash` tool to query the ContextBridge API whenever the user's request falls into any of these 4 categories:

1. **Information Retrieval (Q&A)**: The user asks for specific facts, historical data, or project details that are not general world knowledge (e.g., "What was our Q3 revenue?", "Find the meeting minutes from last Tuesday").
2. **Document Auditing & Compliance**: The user asks you to review, verify, or audit a document/text. **CRITICAL**: You must first search for local "policies", "guidelines", "laws", or "rules" to establish the review criteria before answering.
3. **Contextual Drafting**: The user asks you to write an email, proposal, or report based on past context (e.g., "Draft a proposal using our standard company template", "Write an email based on the product specs").
4. **Troubleshooting & SOPs**: The user asks how to fix an internal error or follow an internal process (e.g., "How do I deploy the backend?", "What is the onboarding process?").

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
