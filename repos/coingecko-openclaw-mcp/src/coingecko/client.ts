import type {
  CategoryMarket,
  CoinGeckoMarketClient,
  CoinsMarket,
  GlobalResponse,
  MarketChartResponse,
  TrendingResponse
} from "./types.js";

interface CoinGeckoProClientOptions {
  apiKey: string;
  baseUrl?: string;
  fetchImpl?: typeof fetch;
}

function withTrailingSlash(value: string): string {
  return value.endsWith("/") ? value : `${value}/`;
}

function appendArrayOrValue(search: URLSearchParams, key: string, value: string | number | string[] | undefined): void {
  if (value === undefined) {
    return;
  }

  if (Array.isArray(value)) {
    search.set(key, value.join(","));
    return;
  }

  search.set(key, String(value));
}

export class CoinGeckoProClient implements CoinGeckoMarketClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly fetchImpl: typeof fetch;

  constructor(options: CoinGeckoProClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = withTrailingSlash(options.baseUrl ?? "https://pro-api.coingecko.com/api/v3");
    this.fetchImpl = options.fetchImpl ?? fetch;
  }

  async getGlobal(): Promise<GlobalResponse> {
    return this.request<GlobalResponse>("global");
  }

  async getCoinsMarkets(params: {
    ids?: string[];
    vsCurrency: string;
    perPage?: number;
    order?: string;
    category?: string;
    priceChangePercentage?: string[];
  }): Promise<CoinsMarket[]> {
    return this.request<CoinsMarket[]>("coins/markets", {
      vs_currency: params.vsCurrency,
      ids: params.ids,
      per_page: params.perPage,
      order: params.order,
      category: params.category,
      sparkline: "false",
      price_change_percentage: params.priceChangePercentage
    });
  }

  async getTrending(): Promise<TrendingResponse> {
    return this.request<TrendingResponse>("search/trending");
  }

  async getCategories(): Promise<CategoryMarket[]> {
    return this.request<CategoryMarket[]>("coins/categories");
  }

  async getMarketChart(coinId: string, params: {
    vsCurrency: string;
    days: number;
  }): Promise<MarketChartResponse> {
    return this.request<MarketChartResponse>(`coins/${coinId}/market_chart`, {
      vs_currency: params.vsCurrency,
      days: params.days
    });
  }

  private async request<T>(path: string, query?: Record<string, string | number | string[] | undefined>): Promise<T> {
    const url = new URL(path, this.baseUrl);

    if (query) {
      Object.entries(query).forEach(([key, value]) => appendArrayOrValue(url.searchParams, key, value));
    }

    const response = await this.fetchImpl(url, {
      method: "GET",
      headers: {
        accept: "application/json",
        "x-cg-pro-api-key": this.apiKey
      }
    });

    if (!response.ok) {
      const body = await response.text();
      throw new Error(`CoinGecko request failed (${response.status} ${response.statusText}): ${body}`);
    }

    return response.json() as Promise<T>;
  }
}
