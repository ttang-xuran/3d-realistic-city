from __future__ import annotations

from typing import List, Optional

try:
    from mcp.client.session import ClientSession
    from mcp.client.sse import sse_client
except Exception:  # pragma: no cover
    ClientSession = None
    aconnect_sse = None


def search_docs(query: str, server_url: Optional[str] = None) -> List[str]:
    if ClientSession is None:
        return [
            "MCP client not available. Install mcp[client] and run again.",
            "Alternatively, use your IDE's MCP integration with the context7 server.",
        ]

    # Placeholder: In practice, context7 exposes tools like `search` or `doc_lookup`.
    # Here we show the call shape; adjust tool name/params to your server.
    async def _run() -> List[str]:
        if not server_url:
            raise RuntimeError("server_url is required for MCP SSE transport")
        # Establish SSE client which yields read and write streams for ClientSession
        async with sse_client(server_url) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                try:
                    result = await session.call_tool(
                        tool_name="search",
                        arguments={"q": query, "source": "autogen-0.7.2"},
                    )
                    texts = []
                    for item in result.get("items", []):
                        texts.append(f"{item.get('title', '')}\n{item.get('snippet', '')}\n{item.get('url', '')}")
                    return texts or ["No results"]
                except Exception as exc:  # pragma: no cover
                    return [f"Error calling MCP search: {exc}"]

    try:
        import anyio

        return anyio.run(_run)
    except Exception as exc:  # pragma: no cover
        return [f"Error running MCP client: {exc}"]
