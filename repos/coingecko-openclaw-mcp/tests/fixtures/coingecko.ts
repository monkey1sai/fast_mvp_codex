export const marketFixture = [
  {
    id: "bitcoin",
    symbol: "btc",
    name: "Bitcoin",
    current_price: 90000,
    market_cap: 1800000000000,
    market_cap_rank: 1,
    total_volume: 42000000000,
    high_24h: 91000,
    low_24h: 87000,
    price_change_percentage_24h: 1.8,
    price_change_percentage_7d_in_currency: 5.4
  },
  {
    id: "ethereum",
    symbol: "eth",
    name: "Ethereum",
    current_price: 4200,
    market_cap: 510000000000,
    market_cap_rank: 2,
    total_volume: 21000000000,
    high_24h: 4250,
    low_24h: 3980,
    price_change_percentage_24h: 3.2,
    price_change_percentage_7d_in_currency: 9.1
  },
  {
    id: "solana",
    symbol: "sol",
    name: "Solana",
    current_price: 205,
    market_cap: 99000000000,
    market_cap_rank: 5,
    total_volume: 6800000000,
    high_24h: 214,
    low_24h: 193,
    price_change_percentage_24h: -4.5,
    price_change_percentage_7d_in_currency: 12.3
  }
] as const;

export const globalFixture = {
  data: {
    active_cryptocurrencies: 15324,
    total_market_cap: { usd: 3200000000000 },
    total_volume: { usd: 135000000000 },
    market_cap_change_percentage_24h_usd: 2.3,
    market_cap_percentage: { btc: 56.2, eth: 16.4 }
  }
} as const;

export const trendingFixture = {
  coins: [
    {
      item: {
        id: "virtual-protocol",
        name: "Virtual Protocol",
        symbol: "VIRTUAL",
        market_cap_rank: 118,
        score: 0,
        data: {
          price: 1.23,
          price_change_percentage_24h: { usd: 18.4 }
        }
      }
    },
    {
      item: {
        id: "aixbt",
        name: "AIXBT",
        symbol: "AIXBT",
        market_cap_rank: 240,
        score: 1,
        data: {
          price: 0.72,
          price_change_percentage_24h: { usd: 12.1 }
        }
      }
    }
  ],
  categories: [
    {
      id: 1,
      name: "AI Agents",
      market_cap_1h_change: 1.9,
      slug: "ai-agents",
      coins_count: 42,
      data: {
        market_cap: 18500000000,
        market_cap_btc: 205000,
        total_volume: 4100000000,
        sparkline: "",
        content: ""
      }
    }
  ]
} as const;

export const categoryFixture = [
  {
    id: "ai-agents",
    name: "AI Agents",
    market_cap: 18500000000,
    market_cap_change_24h: 12.7,
    volume_24h: 4100000000,
    content: "",
    top_3_coins_id: ["virtual-protocol", "aixbt", "ai16z"]
  },
  {
    id: "layer-1",
    name: "Layer 1 (L1)",
    market_cap: 970000000000,
    market_cap_change_24h: 3.1,
    volume_24h: 42000000000,
    content: "",
    top_3_coins_id: ["bitcoin", "ethereum", "solana"]
  },
  {
    id: "meme-token",
    name: "Meme",
    market_cap: 64000000000,
    market_cap_change_24h: -6.2,
    volume_24h: 9700000000,
    content: "",
    top_3_coins_id: ["dogecoin", "shiba-inu", "pepe"]
  }
] as const;

export const marketChartFixture = {
  prices: [
    [1, 180],
    [2, 188],
    [3, 194],
    [4, 203],
    [5, 198],
    [6, 211],
    [7, 217],
    [8, 214],
    [9, 208],
    [10, 205]
  ]
} as const;
