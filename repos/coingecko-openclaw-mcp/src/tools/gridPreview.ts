import type { MarketChartResponse } from "../coingecko/types.js";
import { calculateGrid } from "../lib/grid.js";

export interface GridStrategyPreviewArgs {
  coin_id: string;
  vs_currency?: string;
  capital: number;
  grid_count?: number;
  lookback_days?: number;
  fee_rate?: number;
}

interface GridPreviewClient {
  getMarketChart(coinId: string, params: {
    vsCurrency: string;
    days: number;
  }): Promise<MarketChartResponse>;
}

function round(value: number, digits = 4): number {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

export async function buildGridStrategyPreview(client: GridPreviewClient, args: GridStrategyPreviewArgs) {
  const gridCount = args.grid_count ?? 8;
  const lookbackDays = args.lookback_days ?? 30;
  const feeRate = args.fee_rate ?? 0.001;
  const vsCurrency = args.vs_currency ?? "usd";

  const marketChart = await client.getMarketChart(args.coin_id, {
    vsCurrency,
    days: lookbackDays
  });

  const prices = marketChart.prices.map((entry) => entry[1]);
  const calculation = calculateGrid({
    prices,
    gridCount,
    capital: args.capital,
    feeRate
  });

  const levels = calculation.levels.map((price, index) => ({
    index,
    price,
    bias:
      price < calculation.currentPrice
        ? "accumulate"
        : price > calculation.currentPrice
          ? "distribute"
          : "mid"
  }));

  const agentNotes = [
    `Suggested grid for ${args.coin_id} spans ${calculation.suggestedLower} to ${calculation.suggestedUpper} ${vsCurrency} across ${gridCount} intervals.`,
    `Current price ${calculation.currentPrice} sits against an observed range of ${calculation.observedLow} to ${calculation.observedHigh}.`,
    `Estimated net edge per completed grid is ${(calculation.estimatedNetEdgePct * 100).toFixed(2)}% with ${(feeRate * 100).toFixed(2)}% fee assumption.`
  ];

  if (calculation.warnings[0]) {
    agentNotes.push(`Primary warning: ${calculation.warnings[0]}`);
  } else {
    agentNotes.push("No structural warning triggered from range width, fee edge, or capital-per-grid checks.");
  }

  return {
    generated_at: new Date().toISOString(),
    coin_id: args.coin_id,
    vs_currency: vsCurrency,
    lookback_days: lookbackDays,
    current_price: calculation.currentPrice,
    observed_range: {
      low: calculation.observedLow,
      high: calculation.observedHigh
    },
    strategy_bounds: {
      lower: calculation.suggestedLower,
      upper: calculation.suggestedUpper,
      width_pct: round(calculation.bandWidthPct)
    },
    capital_plan: {
      total_capital: round(args.capital, 2),
      capital_per_grid: calculation.capitalPerGrid
    },
    levels,
    estimated_net_edge_pct: round(calculation.estimatedNetEdgePct),
    warnings: calculation.warnings,
    agent_notes: agentNotes
  };
}
