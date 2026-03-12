export interface GridCalculationInput {
  prices: number[];
  gridCount: number;
  capital: number;
  feeRate: number;
}

export interface GridCalculationResult {
  currentPrice: number;
  observedLow: number;
  observedHigh: number;
  suggestedLower: number;
  suggestedUpper: number;
  bandWidthPct: number;
  estimatedNetEdgePct: number;
  capitalPerGrid: number;
  levels: number[];
  warnings: string[];
}

function round(value: number, digits = 4): number {
  const factor = 10 ** digits;
  return Math.round(value * factor) / factor;
}

function percentile(values: number[], ratio: number): number {
  const sorted = [...values].sort((left, right) => left - right);
  const index = (sorted.length - 1) * ratio;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);

  if (lower === upper) {
    return sorted[lower]!;
  }

  const weight = index - lower;
  return sorted[lower]! * (1 - weight) + sorted[upper]! * weight;
}

export function calculateGrid(input: GridCalculationInput): GridCalculationResult {
  const { capital, feeRate, gridCount, prices } = input;

  if (prices.length < 3) {
    throw new Error("At least three price samples are required to compute a grid preview.");
  }

  if (gridCount < 2) {
    throw new Error("gridCount must be at least 2.");
  }

  const observedLow = Math.min(...prices);
  const observedHigh = Math.max(...prices);
  const currentPrice = prices[prices.length - 1]!;

  let suggestedLower = percentile(prices, 0.15);
  let suggestedUpper = percentile(prices, 0.85);

  if (!(suggestedLower < suggestedUpper)) {
    suggestedLower = observedLow;
    suggestedUpper = observedHigh;
  }

  const step = (suggestedUpper - suggestedLower) / gridCount;
  const levels = Array.from({ length: gridCount + 1 }, (_, index) => round(suggestedLower + step * index));
  const bandWidthPct = (suggestedUpper - suggestedLower) / currentPrice;
  const averageLevel = (suggestedLower + suggestedUpper) / 2;
  const estimatedNetEdgePct = step / averageLevel - feeRate * 2;
  const capitalPerGrid = capital / gridCount;
  const warnings: string[] = [];

  if (currentPrice < suggestedLower || currentPrice > suggestedUpper) {
    warnings.push("Current price sits outside the suggested band; wait for mean re-entry or widen the grid.");
  }

  if (estimatedNetEdgePct <= 0) {
    warnings.push("Round-trip fee assumption erases the estimated per-grid edge.");
  }

  if (bandWidthPct < 0.08) {
    warnings.push("Recent realized range is tight; the grid may overtrade a noisy band.");
  }

  if (capitalPerGrid < 25) {
    warnings.push("Capital per grid is low and may run into exchange minimum order sizes.");
  }

  return {
    currentPrice: round(currentPrice),
    observedLow: round(observedLow),
    observedHigh: round(observedHigh),
    suggestedLower: round(suggestedLower),
    suggestedUpper: round(suggestedUpper),
    bandWidthPct: round(bandWidthPct),
    estimatedNetEdgePct: round(estimatedNetEdgePct),
    capitalPerGrid: round(capitalPerGrid, 2),
    levels,
    warnings
  };
}
