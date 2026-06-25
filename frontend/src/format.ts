import i18n from "./i18n";

function locale(): string {
  return i18n.language ?? "en";
}

export function formatMoney(cents: number, currency: string | null): string {
  return new Intl.NumberFormat(locale(), {
    style: "currency",
    currency: currency ?? "USD",
    maximumFractionDigits: 2
  }).format(cents / 100);
}

export function formatPlaytime(minutes: number): string {
  const hours = Math.floor(minutes / 60);
  if (hours < 1) return `${minutes}m`;
  return `${hours.toLocaleString(locale())}h`;
}

export function formatDateTime(value: string | null): string {
  if (!value) return i18n.t("format.never");
  return new Intl.DateTimeFormat(locale(), {
    dateStyle: "medium",
    timeStyle: "short"
  }).format(new Date(value));
}
