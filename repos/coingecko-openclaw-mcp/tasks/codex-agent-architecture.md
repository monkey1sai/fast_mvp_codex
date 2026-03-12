# Agent Architecture

## Purpose
- Provide CoinGecko Pro market intelligence to OpenClaw-compatible agents through MCP stdio.

## Layers
- `src/coingecko`: authenticated API client
- `src/tools`: agent-facing tool builders
- `src/lib`: reusable calculation helpers
- `src/index.ts`: MCP registration and stdio transport

## Design
- API key stays server-side.
- Tool outputs emphasize context, risk, and opportunity signals.
- Tools remain read-only; no trade execution.
