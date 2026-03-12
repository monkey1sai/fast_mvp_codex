import { describe, expect, it } from "vitest";

import { buildGridStrategyPreview } from "../src/tools/gridPreview.js";
import { marketChartFixture } from "./fixtures/coingecko.js";

describe("buildGridStrategyPreview", () => {
  it("turns historical prices into actionable grid levels", async () => {
    const result = await buildGridStrategyPreview(
      {
        getMarketChart: async () => marketChartFixture
      },
      {
        coin_id: "solana",
        vs_currency: "usd",
        capital: 1000,
        grid_count: 5,
        lookback_days: 14,
        fee_rate: 0.001
      }
    );

    expect(result.coin_id).toBe("solana");
    expect(result.levels).toHaveLength(6);
    expect(result.capital_plan.capital_per_grid).toBe(200);
    expect(result.strategy_bounds.upper).toBeGreaterThan(result.strategy_bounds.lower);
    expect(result.agent_notes.join(" ")).toContain("grid");
  });
});
