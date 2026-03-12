import type { CategoryMarket, TrendingCoin, TrendingResponse } from "../coingecko/types.js";

export interface NarrativeScanArgs {
  vs_currency?: string;
  top_categories?: number;
  include_trending?: boolean;
}

interface NarrativeScanClient {
  getTrending(): Promise<TrendingResponse>;
  getCategories(): Promise<CategoryMarket[]>;
}

function normalizeTrendingCoin(coin: TrendingCoin) {
  return {
    id: coin.item.id,
    name: coin.item.name,
    symbol: coin.item.symbol,
    market_cap_rank: coin.item.market_cap_rank ?? null,
    score: coin.item.score ?? null,
    price: coin.item.data?.price ?? null,
    price_change_percentage_24h: coin.item.data?.price_change_percentage_24h?.usd ?? null
  };
}

function normalizeCategory(category: CategoryMarket) {
  return {
    id: category.id,
    name: category.name,
    market_cap: category.market_cap,
    market_cap_change_24h: category.market_cap_change_24h,
    volume_24h: category.volume_24h,
    top_3_coins_id: category.top_3_coins_id ?? []
  };
}

export async function buildNarrativeScan(client: NarrativeScanClient, args: NarrativeScanArgs) {
  const topCategories = args.top_categories ?? 3;
  const includeTrending = args.include_trending !== false;
  const [categories, trending] = await Promise.all([
    client.getCategories(),
    includeTrending ? client.getTrending() : Promise.resolve(null)
  ]);

  const sortedByMomentum = [...categories].sort((left, right) => right.market_cap_change_24h - left.market_cap_change_24h);
  const hotCategories = sortedByMomentum.filter((category) => category.market_cap_change_24h > 0).slice(0, topCategories);
  const riskCategories = [...categories]
    .sort((left, right) => left.market_cap_change_24h - right.market_cap_change_24h)
    .filter((category) => category.market_cap_change_24h < 0)
    .slice(0, Math.min(2, topCategories));

  const trendingCoins = includeTrending
    ? (trending?.coins ?? []).map(normalizeTrendingCoin).slice(0, 5)
    : [];

  const agentNotes = [
    hotCategories[0]
      ? `${hotCategories[0].name} is the strongest narrative at ${hotCategories[0].market_cap_change_24h.toFixed(2)}% over 24h with ${new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact", maximumFractionDigits: 2 }).format(hotCategories[0].volume_24h)} volume.`
      : "No positive category momentum was returned by CoinGecko.",
    riskCategories[0]
      ? `${riskCategories[0].name} is the weakest category at ${riskCategories[0].market_cap_change_24h.toFixed(2)}% over 24h and can act as a risk-off monitor.`
      : "No negative category momentum was returned by CoinGecko.",
    trendingCoins[0]
      ? `${trendingCoins[0].name} currently tops the attention list with ${trendingCoins[0].price_change_percentage_24h?.toFixed(2) ?? "n/a"}% 24h price change.`
      : "Trending coin attention is disabled or not available."
  ];

  return {
    generated_at: new Date().toISOString(),
    vs_currency: args.vs_currency ?? "usd",
    hot_categories: hotCategories.map(normalizeCategory),
    risk_categories: riskCategories.map(normalizeCategory),
    trending_coins: trendingCoins,
    opportunity_map: hotCategories.map((category) => ({
      narrative: category.name,
      reason: `${category.market_cap_change_24h.toFixed(2)}% 24h category momentum on ${new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact", maximumFractionDigits: 2 }).format(category.volume_24h)} volume.`,
      related_assets: category.top_3_coins_id ?? []
    })),
    agent_notes: agentNotes
  };
}
