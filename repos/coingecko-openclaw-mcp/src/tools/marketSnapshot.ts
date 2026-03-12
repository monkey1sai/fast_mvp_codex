import type { CoinsMarket, GlobalResponse } from "../coingecko/types.js";

export interface MarketSnapshotArgs {
  coin_ids?: string[];
  vs_currency?: string;
  include_global?: boolean;
  top_assets?: number;
}

interface MarketSnapshotClient {
  getGlobal(): Promise<GlobalResponse>;
  getCoinsMarkets(params: {
    ids?: string[];
    vsCurrency: string;
    perPage?: number;
    order?: string;
    category?: string;
    priceChangePercentage?: string[];
  }): Promise<CoinsMarket[]>;
}

function formatUsd(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: value >= 1_000_000_000 ? "compact" : "standard",
    maximumFractionDigits: 2
  }).format(value);
}

function formatPct(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "n/a";
  }

  return `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;
}

function pickStrongest(assets: CoinsMarket[], direction: "max" | "min"): CoinsMarket {
  const comparator = direction === "max"
    ? (left: CoinsMarket, right: CoinsMarket) => (left.price_change_percentage_24h ?? Number.NEGATIVE_INFINITY) - (right.price_change_percentage_24h ?? Number.NEGATIVE_INFINITY)
    : (left: CoinsMarket, right: CoinsMarket) => (left.price_change_percentage_24h ?? Number.POSITIVE_INFINITY) - (right.price_change_percentage_24h ?? Number.POSITIVE_INFINITY);

  return [...assets].sort(comparator).at(direction === "max" ? -1 : 0)!;
}

export async function buildMarketSnapshot(client: MarketSnapshotClient, args: MarketSnapshotArgs) {
  const vsCurrency = args.vs_currency ?? "usd";
  const coinIds = args.coin_ids;
  const topAssets = args.top_assets ?? (coinIds?.length ?? 8);

  const [globalData, assets] = await Promise.all([
    args.include_global === false ? Promise.resolve(null) : client.getGlobal(),
    client.getCoinsMarkets({
      ids: coinIds,
      vsCurrency,
      perPage: topAssets,
      order: "market_cap_desc",
      priceChangePercentage: ["24h", "7d"]
    })
  ]);

  if (assets.length === 0) {
    throw new Error("CoinGecko returned no market data for the requested asset set.");
  }

  const marketCapLeader = [...assets].sort((left, right) => right.market_cap - left.market_cap)[0]!;
  const strongest = pickStrongest(assets, "max");
  const weakest = pickStrongest(assets, "min");
  const positiveBreadth = assets.filter((asset) => (asset.price_change_percentage_24h ?? 0) > 0).length / assets.length;

  const global = globalData
    ? {
        active_cryptocurrencies: globalData.data.active_cryptocurrencies,
        total_market_cap: globalData.data.total_market_cap[vsCurrency],
        total_volume: globalData.data.total_volume[vsCurrency],
        market_cap_change_percentage_24h: globalData.data.market_cap_change_percentage_24h_usd,
        btc_dominance: globalData.data.market_cap_percentage.btc,
        market_sentiment:
          globalData.data.market_cap_change_percentage_24h_usd > 1
            ? "risk-on"
            : globalData.data.market_cap_change_percentage_24h_usd < -1
              ? "risk-off"
              : "balanced"
      }
    : null;

  const agentNotes = [
    `${marketCapLeader.name} remains the market-cap anchor at ${formatUsd(marketCapLeader.market_cap)}.`,
    `${strongest.name} leads 24h momentum at ${formatPct(strongest.price_change_percentage_24h)} while ${weakest.name} is the weakest mover at ${formatPct(weakest.price_change_percentage_24h)}.`,
    global
      ? `Global market cap is ${formatUsd(global.total_market_cap)} with ${global.market_sentiment} tone, BTC dominance ${global.btc_dominance.toFixed(1)}%, and positive breadth ${(positiveBreadth * 100).toFixed(0)}%.`
      : `Positive breadth across the requested basket is ${(positiveBreadth * 100).toFixed(0)}%.`
  ];

  return {
    generated_at: new Date().toISOString(),
    vs_currency: vsCurrency,
    requested_coin_ids: coinIds ?? [],
    global,
    leaders: {
      market_cap_leader: marketCapLeader.id,
      strongest_24h_mover: strongest.id,
      weakest_24h_mover: weakest.id
    },
    assets: assets.map((asset) => ({
      id: asset.id,
      symbol: asset.symbol,
      name: asset.name,
      current_price: asset.current_price,
      market_cap: asset.market_cap,
      market_cap_rank: asset.market_cap_rank,
      total_volume: asset.total_volume,
      high_24h: asset.high_24h,
      low_24h: asset.low_24h,
      price_change_percentage_24h: asset.price_change_percentage_24h ?? null,
      price_change_percentage_7d: asset.price_change_percentage_7d_in_currency ?? null
    })),
    agent_notes: agentNotes
  };
}
