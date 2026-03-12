import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import * as z from "zod/v4";

import { CoinGeckoProClient } from "./coingecko/client.js";
import { buildGridStrategyPreview } from "./tools/gridPreview.js";
import { buildMarketSnapshot } from "./tools/marketSnapshot.js";
import { buildNarrativeScan } from "./tools/narrativeScan.js";

function toToolResult<T extends Record<string, unknown>>(value: T) {
  return {
    content: [
      {
        type: "text" as const,
        text: JSON.stringify(value, null, 2)
      }
    ],
    structuredContent: value
  };
}

export function createServer(client: CoinGeckoProClient): McpServer {
  const server = new McpServer({
    name: "coingecko-openclaw-mcp",
    version: "0.1.0"
  });

  server.registerTool("cg_market_snapshot", {
    title: "CoinGecko Market Snapshot",
    description: "Get market-cap leaders, directional breadth, and global crypto context for a basket of coins.",
    inputSchema: {
      coin_ids: z.array(z.string()).min(1).max(25).optional().describe("Optional CoinGecko coin ids to inspect. Defaults to top market-cap assets."),
      vs_currency: z.string().default("usd").describe("Quote currency such as usd, twd, or btc."),
      include_global: z.boolean().default(true).describe("Include global market-cap, volume, and BTC dominance context."),
      top_assets: z.number().int().min(1).max(25).optional().describe("How many assets to fetch when coin_ids are omitted.")
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  }, async (args) => toToolResult(await buildMarketSnapshot(client, args)));

  server.registerTool("cg_narrative_scan", {
    title: "CoinGecko Narrative Scan",
    description: "Scan category momentum, trending attention, and opportunity/risk narratives across the crypto market.",
    inputSchema: {
      vs_currency: z.string().default("usd").describe("Quote currency label for downstream summaries."),
      top_categories: z.number().int().min(1).max(10).default(3).describe("Number of strongest categories to surface."),
      include_trending: z.boolean().default(true).describe("Include CoinGecko trending-coin attention data.")
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  }, async (args) => toToolResult(await buildNarrativeScan(client, args)));

  server.registerTool("cg_grid_strategy_preview", {
    title: "CoinGecko Grid Strategy Preview",
    description: "Turn recent historical prices into a non-custodial grid band, level plan, and warning set.",
    inputSchema: {
      coin_id: z.string().describe("CoinGecko coin id such as bitcoin, ethereum, or solana."),
      vs_currency: z.string().default("usd").describe("Quote currency."),
      capital: z.number().positive().describe("Capital budget for the grid plan."),
      grid_count: z.number().int().min(2).max(50).default(8).describe("Number of grid intervals."),
      lookback_days: z.number().int().min(1).max(365).default(30).describe("Historical window in days."),
      fee_rate: z.number().min(0).max(0.05).default(0.001).describe("Estimated one-way fee rate as decimal, e.g. 0.001 for 0.1%.")
    },
    annotations: {
      readOnlyHint: true,
      destructiveHint: false,
      idempotentHint: true,
      openWorldHint: true
    }
  }, async (args) => toToolResult(await buildGridStrategyPreview(client, args)));

  return server;
}
