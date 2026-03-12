import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

import { CoinGeckoProClient } from "./coingecko/client.js";
import { loadConfig } from "./config.js";
import { createServer } from "./index.js";

async function main(): Promise<void> {
  const config = loadConfig();
  const client = new CoinGeckoProClient({
    apiKey: config.apiKey,
    baseUrl: config.apiBaseUrl
  });
  const server = createServer(client);
  const transport = new StdioServerTransport();

  await server.connect(transport);
  console.error("coingecko-openclaw-mcp running on stdio");
}

main().catch((error) => {
  console.error("MCP server error:", error);
  process.exit(1);
});
