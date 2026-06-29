import { describe, expect, it } from "vitest";
import { formatDateTime, formatMoney, formatPlaytime } from "./format";

describe("formatMoney", () => {
  it("formats cents into currency string", () => {
    expect(formatMoney(1999, "USD")).toBe("$19.99");
  });

  it("defaults to USD when currency is null", () => {
    expect(formatMoney(0, null)).toBe("$0.00");
  });

  it("handles zero cents", () => {
    expect(formatMoney(0, "USD")).toBe("$0.00");
  });

  it("supports other currencies", () => {
    expect(formatMoney(2999, "EUR")).toBe("€29.99");
  });
});

describe("formatPlaytime", () => {
  it("formats minutes under 60 with m suffix", () => {
    expect(formatPlaytime(30)).toBe("30m");
  });

  it("formats exactly 60 minutes as 1h", () => {
    expect(formatPlaytime(60)).toBe("1h");
  });

  it("formats hours with thousands separator", () => {
    expect(formatPlaytime(60000)).toBe("1,000h");
  });

  it("formats zero minutes as 0m", () => {
    expect(formatPlaytime(0)).toBe("0m");
  });
});

describe("formatDateTime", () => {
  it("returns Never for null", () => {
    expect(formatDateTime(null)).toBe("Never");
  });

  it("formats a valid ISO date string", () => {
    const result = formatDateTime("2026-06-16T10:00:00Z");
    expect(result).not.toBe("Never");
    expect(result).toContain("2026");
  });
});
