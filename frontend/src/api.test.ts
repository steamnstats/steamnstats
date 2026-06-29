import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import {
  api,
  clearTokens,
  getAccessToken,
  getRefreshToken,
  setTokens,
} from "./api";

beforeEach(() => {
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("token management", () => {
  it("returns null when no tokens are set", () => {
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });

  it("stores and retrieves tokens", () => {
    setTokens("access-123", "refresh-456");
    expect(getAccessToken()).toBe("access-123");
    expect(getRefreshToken()).toBe("refresh-456");
  });

  it("clears tokens", () => {
    setTokens("access-123", "refresh-456");
    clearTokens();
    expect(getAccessToken()).toBeNull();
    expect(getRefreshToken()).toBeNull();
  });
});

describe("api.request", () => {
  it("sends Authorization header when token is set", async () => {
    setTokens("access-123", "refresh-456");
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    await api.me();

    expect(fetchMock).toHaveBeenCalledOnce();
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect((init.headers as Record<string, string>).Authorization).toBe(
      "Bearer access-123"
    );
  });

  it("omits Authorization header when no token", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    await api.me();

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect((init.headers as Record<string, string>).Authorization).toBeUndefined();
  });

  it("throws on non-ok response", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ detail: "Unauthorized" }), {
        status: 401,
        headers: { "Content-Type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(api.me()).rejects.toThrow("Unauthorized");
  });

  it("throws with statusText when body is not JSON", async () => {
    const fetchMock = vi.fn(async () =>
      new Response("Internal Server Error", { status: 500 })
    );
    vi.stubGlobal("fetch", fetchMock);

    await expect(api.me()).rejects.toThrow();
  });

  it("returns undefined for 204 status", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(null, { status: 204 })
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await api.logout("refresh-token");
    expect(result).toBeUndefined();
  });

  it("library unwraps items from response", async () => {
    const items = [{ game: { app_id: 1 }, playtime_forever_minutes: 10 }];
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ items }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await api.library();
    expect(result).toEqual(items);
  });

  it("sync sends POST method", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(JSON.stringify({ id: "job-1", status: "succeeded" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );
    vi.stubGlobal("fetch", fetchMock);

    await api.sync();

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.method).toBe("POST");
  });

  it("refresh sends POST with refresh_token in body", async () => {
    const fetchMock = vi.fn(async () =>
      new Response(
        JSON.stringify({ access_token: "new-a", refresh_token: "new-r" }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );
    vi.stubGlobal("fetch", fetchMock);

    const result = await api.refresh("old-refresh");
    expect(result.access_token).toBe("new-a");
    expect(result.refresh_token).toBe("new-r");

    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect(init.method).toBe("POST");
    expect(JSON.parse(init.body as string).refresh_token).toBe("old-refresh");
  });
});
