import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { connectServer } from "./mcp_server.js";

async function main() {
    const transport = new StdioServerTransport();
    await connectServer(transport);
    console.error("Spectra Dayoff MCP Server running on stdio");
}
  
main().catch((error) => {
    console.error("Fatal error in main():", error);
    process.exit(1);
});
