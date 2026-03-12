const DEFAULT_BASE_URL = "https://pro-api.coingecko.com/api/v3";

export interface AppConfig {
  apiKey: string;
  apiBaseUrl: string;
}

export function loadConfig(env: NodeJS.ProcessEnv = process.env): AppConfig {
  const apiKey = env.COINGECKO_PRO_API_KEY;

  if (!apiKey) {
    throw new Error("Missing COINGECKO_PRO_API_KEY in environment.");
  }

  return {
    apiKey,
    apiBaseUrl: env.COINGECKO_API_BASE_URL ?? DEFAULT_BASE_URL
  };
}
