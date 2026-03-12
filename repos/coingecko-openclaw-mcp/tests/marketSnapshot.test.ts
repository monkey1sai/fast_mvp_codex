import { describe, expect, it } from "vitest";

import { buildMarketSnapshot } from "../src/tools/marketSnapshot.js";
import { globalFixture, marketFixture } from "./fixtures/coingecko.js";

describe("buildMarketSnapshot", () => {
  it("summarizes market leaders and directional signals for an agent", async () => {
    const result = await buildMarketSnapshot(
      {
        getGlobal: async () => globalFixture,
        getCoinsMarkets: async () => [...marketFixture]
      },
      {
        coin_ids: ["bitcoin", "ethereum", "solana"],
        vs_currency: "usd",
        include_global: true
      }
    );

    expect(result.global?.market_sentiment).toBe("risk-on");
    expect(result.leaders.market_cap_leader).toBe("bitcoin");
    expect(result.leaders.strongest_24h_mover).toBe("ethereum");
    expect(result.leaders.weakest_24h_mover).toBe("solana");
    expect(result.assets).toHaveLength(3);
    expect(result.agent_notes[0]).toContain("Bitcoin");
  });
});
