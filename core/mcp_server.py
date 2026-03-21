import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolRequest
from core.factories import initialize_system
from core.config import init_workspace

app = Server("context-bridge")
_context_manager = None

def get_context_manager():
    global _context_manager
    if _context_manager is None:
        _context_manager = initialize_system()
    return _context_manager

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="search_documents",
            description="Search through local Office documents (Word, Excel) for relevant information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant information in documents."
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "search_documents":
        query = arguments.get("query")
        if not query:
            return [TextContent(type="text", text="Error: query is required.")]
        
        context_manager = get_context_manager()
        results = context_manager.recursive_retrieve(query)
        
        if not results:
            return [TextContent(type="text", text="No relevant information found.")]
            
        response_text = "Found the following relevant documents:\n\n"
        for res in results:
            source = res.get('uri', 'Unknown')
            abstract = res.get('abstract', '')
            excerpts = res.get('relevant_excerpts', [])
            
            response_text += f"### Source: {source}\n"
            response_text += f"**Abstract:** {abstract}\n"
            response_text += "**Relevant Excerpts:**\n"
            for excerpt in excerpts:
                response_text += f"- {excerpt}\n"
            response_text += "\n"
            
        return [TextContent(type="text", text=response_text)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    init_workspace()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
