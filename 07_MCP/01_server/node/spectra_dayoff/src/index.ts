import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const server = new McpServer({
    name: "spectra-dayoff",
    version: "1.0.0",
    capabilities: {
        resources: {},
        tools: {},
    },
});


server.tool(
    "get-current-date",
    "현재 날짜를 가져온다.",
    {},
    async () => {
        const currentDate = new Date().toISOString().split('T')[0];
        return {
            content: [
                {
                    type: "text", 
                    text: currentDate
                }
            ]
        };
    },
);

server.tool(
    "get-dayoff",
    "연차, 휴가를 조회한다.",
    {
        startDate: z.string().describe("시작 날짜 (예: 2025-04-01)"),
        endDate: z.string().describe("종료 날짜 (예: 2025-04-01)"),
    },
    async ({ startDate, endDate }) => {
        return {
            content: [
                {
                    type: "text",
                    text: "서정현: 연차 (2025-04-01)"
                }
            ]
        };
    },
);

async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Spectra Dayoff MCP Server running on stdio");
  }
  
  main().catch((error) => {
    console.error("Fatal error in main():", error);
    process.exit(1);
  });