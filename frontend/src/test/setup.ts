import "@testing-library/jest-dom/vitest";

Object.defineProperty(window, "matchMedia", {
  value: (query: string) => ({
    matches: false,
    media: query,
    onchange: null,
    addEventListener: () => {},
    removeEventListener: () => {},
    addListener: () => {},
    removeListener: () => {},
    dispatchEvent: () => false
  }),
  configurable: true
});

const storage = new Map<string, string>();

Object.defineProperty(window, "localStorage", {
  value: {
    clear: () => storage.clear(),
    getItem: (key: string) => storage.get(key) ?? null,
    removeItem: (key: string) => storage.delete(key),
    setItem: (key: string, value: string) => storage.set(key, value)
  },
  configurable: true
});

Object.defineProperty(globalThis, "localStorage", {
  value: window.localStorage,
  configurable: true
});
