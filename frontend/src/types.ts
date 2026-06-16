export type User = {
  steam_id: string;
  persona_name: string | null;
  avatar_url: string | null;
  profile_url: string | null;
  last_login_at: string;
};

export type Game = {
  app_id: number;
  name: string;
  header_image: string | null;
  current_price_cents: number | null;
  initial_price_cents: number | null;
  discount_percent: number | null;
  currency: string | null;
  is_free: boolean;
  lowest_price_cents: number | null;
  metadata_fetched_at: string | null;
};

export type LibraryEntry = {
  game: Game;
  playtime_forever_minutes: number;
  playtime_2weeks_minutes: number;
  last_played_at: string | null;
  last_synced_at: string;
};

export type Summary = {
  estimated_value_cents: number;
  currency: string | null;
  owned_games: number;
  priced_games: number;
  unavailable_prices: number;
  free_games: number;
  total_playtime_minutes: number;
  most_played: Array<{
    app_id: number;
    name: string;
    playtime_forever_minutes: number;
    header_image: string | null;
  }>;
  last_synced_at: string | null;
};

export type SyncJob = {
  id: string;
  status: "queued" | "running" | "succeeded" | "failed";
  games_seen: number;
  games_priced: number;
  unavailable_prices: number;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
};
