export interface CoinsMarket {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number | null;
  total_volume: number;
  high_24h?: number;
  low_24h?: number;
  price_change_percentage_24h?: number | null;
  price_change_percentage_7d_in_currency?: number | null;
}

export interface GlobalResponse {
  data: {
    active_cryptocurrencies: number;
    total_market_cap: Record<string, number>;
    total_volume: Record<string, number>;
    market_cap_change_percentage_24h_usd: number;
    market_cap_percentage: Record<string, number>;
  };
}

export interface TrendingCoin {
  item: {
    id: string;
    name: string;
    symbol: string;
    market_cap_rank?: number | null;
    score?: number;
    data?: {
      price?: number;
      price_change_percentage_24h?: Record<string, number>;
    };
  };
}

export interface TrendingCategory {
  id: number;
  name: string;
  slug?: string;
  market_cap_1h_change?: number;
  coins_count?: number;
  data?: {
    market_cap?: number;
    market_cap_btc?: number;
    total_volume?: number;
  };
}

export interface TrendingResponse {
  coins: ReadonlyArray<TrendingCoin>;
  categories?: ReadonlyArray<TrendingCategory>;
}

export interface CategoryMarket {
  id: string;
  name: string;
  market_cap: number;
  market_cap_change_24h: number;
  volume_24h: number;
  content?: string;
  top_3_coins_id?: ReadonlyArray<string>;
}

export interface MarketChartResponse {
  prices: ReadonlyArray<readonly [number, number]>;
}

export interface CoinGeckoMarketClient {
  getGlobal(): Promise<GlobalResponse>;
  getCoinsMarkets(params: {
    ids?: string[];
    vsCurrency: string;
    perPage?: number;
    order?: string;
    category?: string;
    priceChangePercentage?: string[];
  }): Promise<CoinsMarket[]>;
  getTrending(): Promise<TrendingResponse>;
  getCategories(): Promise<CategoryMarket[]>;
  getMarketChart(coinId: string, params: {
    vsCurrency: string;
    days: number;
  }): Promise<MarketChartResponse>;
}
