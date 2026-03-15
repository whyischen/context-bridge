import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolRequest
from core.factories import initialize_system
from core.config import init_workspace

app = Server("context-bridge")
context_manager = None

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
        
        global context_manager
        if context_manager is None:
            context_manager = initialize_system()
            
        results = context_manager.recursive_retrieve(query)
        
        if not results:
            return [TextContent(type="text", text="No relevant information found.")]
            
        response_text = "Found the following relevant excerpts:\n\n"
        for res in results:
            source = res.get('uri', 'Unknown')
            content = res.get('content', '')
            response_text += f"--- From {source} ---\n{content}\n\n"
            
        return [TextContent(type="text", text=response_text)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    init_workspace()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
