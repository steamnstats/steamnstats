import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const user = {
  steam_id: "76561198000000000",
  persona_name: "Tester",
  avatar_url: null,
  profile_url: null,
  last_login_at: "2026-06-16T10:00:00Z"
};

const summary = {
  estimated_value_cents: 3999,
  currency: "USD",
  owned_games: 2,
  priced_games: 2,
  unavailable_prices: 0,
  free_games: 1,
  total_playtime_minutes: 600,
  most_played: [
    {
      app_id: 10,
      name: "Counter-Strike",
      playtime_forever_minutes: 500,
      header_image: null
    }
  ],
  last_synced_at: "2026-06-16T10:00:00Z"
};

const library = {
  items: [
    {
      game: {
        app_id: 10,
        name: "Counter-Strike",
        header_image: null,
        current_price_cents: 999,
        initial_price_cents: 999,
        discount_percent: 0,
        currency: "USD",
        is_free: false,
        lowest_price_cents: null,
        metadata_fetched_at: "2026-06-16T10:00:00Z"
      },
      playtime_forever_minutes: 500,
      playtime_2weeks_minutes: 0,
      last_played_at: null,
      last_synced_at: "2026-06-16T10:00:00Z"
    },
    {
      game: {
        app_id: 20,
        name: "Portal",
        header_image: null,
        current_price_cents: 2999,
        initial_price_cents: 2999,
        discount_percent: 0,
        currency: "USD",
        is_free: false,
        lowest_price_cents: null,
        metadata_fetched_at: "2026-06-16T10:00:00Z"
      },
      playtime_forever_minutes: 100,
      playtime_2weeks_minutes: 0,
      last_played_at: null,
      last_synced_at: "2026-06-16T10:00:00Z"
    }
  ]
};

beforeEach(() => {
  localStorage.clear();
  window.history.replaceState({}, "", "/");
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/me")) return json(user);
      if (url.endsWith("/me/summary")) return json(summary);
      if (url.endsWith("/me/library")) return json(library);
      if (url.endsWith("/me/sync")) {
        return json({
          id: "job-1",
          status: "succeeded",
          games_seen: 2,
          games_priced: 2,
          unavailable_prices: 0,
          error: null,
          created_at: "2026-06-16T10:00:00Z",
          started_at: "2026-06-16T10:00:00Z",
          finished_at: "2026-06-16T10:00:00Z"
        });
      }
      return json({}, 404);
    })
  );
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("App", () => {
  it("renders login when unauthenticated", () => {
    render(<App />);
    expect(screen.getByRole("link", { name: /sign in with steam/i })).toBeInTheDocument();
  });

  it("renders dashboard data when authenticated", async () => {
    localStorage.setItem("steamnstats.accessToken", "access");
    localStorage.setItem("steamnstats.refreshToken", "refresh");

    render(<App />);

    await screen.findByText("$39.99");
    expect(screen.getByText("$39.99")).toBeInTheDocument();
    expect(screen.getAllByText("Counter-Strike").length).toBeGreaterThan(0);

    await userEvent.click(screen.getByRole("button", { name: /user menu/i }));
    expect(screen.getByText("Tester")).toBeInTheDocument();
  });

  it("filters library rows", async () => {
    localStorage.setItem("steamnstats.accessToken", "access");
    localStorage.setItem("steamnstats.refreshToken", "refresh");

    render(<App />);
    await screen.findAllByText("Counter-Strike");

    await userEvent.type(screen.getByPlaceholderText("Search games"), "portal");

    await waitFor(() => {
      const table = screen.getByRole("table");
      expect(within(table).queryByText("Counter-Strike")).not.toBeInTheDocument();
      expect(within(table).getByText("Portal")).toBeInTheDocument();
    });
  });
});

function json(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}
