import { describe, expect, it } from "vitest";

import { buildNarrativeScan } from "../src/tools/narrativeScan.js";
import { categoryFixture, trendingFixture } from "./fixtures/coingecko.js";

describe("buildNarrativeScan", () => {
  it("identifies hot narratives, laggards, and opportunity notes", async () => {
    const result = await buildNarrativeScan(
      {
        getTrending: async () => trendingFixture,
        getCategories: async () => [...categoryFixture]
      },
      {
        vs_currency: "usd",
        top_categories: 2,
        include_trending: true
      }
    );

    expect(result.hot_categories[0].id).toBe("ai-agents");
    expect(result.risk_categories[0].id).toBe("meme-token");
    expect(result.trending_coins[0].id).toBe("virtual-protocol");
    expect(result.agent_notes.join(" ")).toContain("AI Agents");
  });
});
