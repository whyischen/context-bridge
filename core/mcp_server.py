import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, CallToolRequest
from core.factories import initialize_system
from core.config import init_workspace, get_watch_dirs, PARSED_DOCS_DIR
from core.utils.path_resolver import PathResolver

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
            description="Search through local Office documents (Word, Excel, PDF) for relevant information. Supports advanced reranking with BM25, keyword matching, and position scoring for improved relevance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to find relevant information in documents."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (optional, uses config default if not specified).",
                        "default": None
                    },
                    "min_similarity": {
                        "type": "number",
                        "description": "Minimum similarity threshold 0.0-1.0 (optional, uses config default if not specified).",
                        "default": None
                    },
                    "enable_rerank": {
                        "type": "boolean",
                        "description": "Enable advanced reranking with BM25 + keywords + position scoring (default: true).",
                        "default": True
                    },
                    "explain": {
                        "type": "boolean",
                        "description": "Include detailed score breakdown and matched keywords in results (default: false).",
                        "default": False
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
        
        # Extract optional parameters
        top_k = arguments.get("top_k")
        min_similarity = arguments.get("min_similarity")
        enable_rerank = arguments.get("enable_rerank", True)
        explain = arguments.get("explain", False)
        
        context_manager = get_context_manager()
        results = context_manager.recursive_retrieve(
            query=query,
            top_k=top_k,
            min_similarity=min_similarity,
            enable_rerank=enable_rerank,
            explain=explain
        )
        
        if not results:
            return [TextContent(type="text", text="No relevant information found.")]
        
        # Initialize PathResolver and resolve paths for all results
        path_resolver = PathResolver({
            'watch_dirs': get_watch_dirs(),
            'parsed_docs_dir': PARSED_DOCS_DIR
        })
        
        for res in results:
            filename = res.get('filename', 'Unknown')
            uri = res.get('uri', 'Unknown')
            try:
                full_content_path = path_resolver.resolve_path(filename, uri)
                res['full_content_path'] = full_content_path
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to resolve path for {filename}: {e}")
                res['full_content_path'] = ""
            
        response_text = "Found the following relevant documents:\n\n"
        for idx, res in enumerate(results, 1):
            source = res.get('uri', 'Unknown')
            filename = res.get('filename', 'Unknown')
            abstract = res.get('abstract', '')
            excerpts = res.get('relevant_excerpts', [])
            score = res.get('score', 0.0)
            full_content_path = res.get('full_content_path', '')
            
            response_text += f"### {idx}. {filename}\n"
            response_text += f"**Source:** {source}\n"
            
            # Add path information
            if full_content_path:
                response_text += f"**File Path:** {full_content_path}\n"
            else:
                response_text += f"**File Path:** Not available\n"
            
            response_text += f"**Relevance Score:** {score*100:.1f}%\n"
            
            # Add score breakdown if explain mode is enabled
            if explain and 'score_breakdown' in res:
                breakdown = res['score_breakdown']
                response_text += f"**Score Breakdown:**\n"
                response_text += f"  - Semantic: {breakdown['semantic']*100:.1f}%\n"
                response_text += f"  - BM25: {breakdown['bm25']*100:.1f}%\n"
                response_text += f"  - Keywords: {breakdown['keyword']*100:.1f}%\n"
                response_text += f"  - Position: {breakdown['position']*100:.1f}%\n"
                response_text += f"  - Title: {breakdown['title']*100:.1f}%\n"
                
                # Show matched keywords
                if 'matched_keywords' in res:
                    matched_kw = res['matched_keywords']
                    kw_list = ", ".join([f"{k}({v})" for k, v in list(matched_kw.items())[:5]])
                    response_text += f"**Matched Keywords:** {kw_list}\n"
            
            response_text += f"**Abstract:** {abstract}\n"
            response_text += "**Relevant Excerpts:**\n"
            for excerpt in excerpts[:3]:  # Limit to 3 excerpts per document
                response_text += f"- {excerpt}\n"
            if len(excerpts) > 3:
                response_text += f"... and {len(excerpts) - 3} more excerpts\n"
            response_text += "\n"
            
        return [TextContent(type="text", text=response_text)]
    
    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    init_workspace()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

def start_mcp_server(port=None):
    """
    Entry point for starting the MCP server.
    Note: stdio transport doesn't use the port, but kept for API compatibility.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    start_mcp_server()
