# TODO

## Objective
- Build an OpenClaw-friendly MCP server that exposes three high-value CoinGecko Pro tools for crypto agents.

## Scope
- `cg_market_snapshot`
- `cg_narrative_scan`
- `cg_grid_strategy_preview`

## Progress
- [x] Bootstrap repo structure
- [x] Add failing tests
- [x] Implement CoinGecko Pro client
- [x] Implement the three MCP tools
- [x] Document OpenClaw integration
- [x] Verify build and tests

## Review
- Keep outputs structured enough for downstream LLMs without hard-coding business conclusions.
- Keep OpenClaw integration honest: register the MCP server on the gateway/agent side, not via ACP bridge per-session metadata.

## Verification
- `npm run build`
- `npm test`
