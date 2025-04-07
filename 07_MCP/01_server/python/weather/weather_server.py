from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "서울은 항상 맑아요~~"

if __name__ == "__main__":
    # mcp.run(transport="stdio")
    mcp.run(transport="sse")