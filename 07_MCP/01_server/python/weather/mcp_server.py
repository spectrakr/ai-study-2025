from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"{location}은 항상 맑아요~~"


def run_server(transport: str = "stdio"):
    """MCP 서버를 실행합니다.

    Args:
        transport: 통신 방식 ("stdio" 또는 "sse")
    """
    mcp.run(transport=transport)
