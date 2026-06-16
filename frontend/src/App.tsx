import {
  BarChart3,
  CircleDollarSign,
  Clock3,
  Database,
  Gamepad2,
  LibraryBig,
  LogOut,
  RefreshCw,
  Search,
  ShieldCheck
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { api, clearTokens, getAccessToken, getRefreshToken, setTokens } from "./api";
import logoMark from "./assets/steamnstats-logo.svg";
import { formatDateTime, formatMoney, formatPlaytime } from "./format";
import type { LibraryEntry, Summary, User } from "./types";

type LoadState = "idle" | "loading" | "loaded" | "error";

function useAuthCallback(): boolean {
  const [handled, setHandled] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const accessToken = params.get("access_token");
    const refreshToken = params.get("refresh_token");
    if (accessToken && refreshToken) {
      setTokens(accessToken, refreshToken);
      window.history.replaceState({}, document.title, "/");
    }
    setHandled(true);
  }, []);

  return handled;
}

export function App() {
  const callbackHandled = useAuthCallback();
  const [isAuthenticated, setAuthenticated] = useState(Boolean(getAccessToken()));
  const [user, setUser] = useState<User | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [library, setLibrary] = useState<LibraryEntry[]>([]);
  const [state, setState] = useState<LoadState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [isSyncing, setSyncing] = useState(false);
  const [filter, setFilter] = useState("");

  async function loadDashboard() {
    if (!getAccessToken()) return;
    setState("loading");
    setError(null);
    try {
      const [me, nextSummary, nextLibrary] = await Promise.all([
        api.me(),
        api.summary(),
        api.library()
      ]);
      setUser(me);
      setSummary(nextSummary);
      setLibrary(nextLibrary);
      setAuthenticated(true);
      setState("loaded");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard");
      setState("error");
    }
  }

  useEffect(() => {
    if (!callbackHandled) return;

    if (isAuthenticated) {
      void loadDashboard();
      return;
    }

    if (getAccessToken()) {
      setAuthenticated(true);
    }
  }, [callbackHandled, isAuthenticated]);

  async function handleSync() {
    setSyncing(true);
    setError(null);
    try {
      await api.sync();
      await loadDashboard();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sync Steam library");
    } finally {
      setSyncing(false);
    }
  }

  async function handleLogout() {
    const refreshToken = getRefreshToken();
    if (refreshToken) {
      await api.logout(refreshToken).catch(() => undefined);
    }
    clearTokens();
    setAuthenticated(false);
    setUser(null);
    setSummary(null);
    setLibrary([]);
  }

  const filteredLibrary = useMemo(() => {
    const query = filter.trim().toLowerCase();
    const sorted = [...library].sort(
      (a, b) => b.playtime_forever_minutes - a.playtime_forever_minutes
    );
    if (!query) return sorted;
    return sorted.filter((entry) => entry.game.name.toLowerCase().includes(query));
  }, [filter, library]);

  if (!callbackHandled) {
    return <ShellSkeleton />;
  }

  if (!isAuthenticated) {
    return <LoginScreen />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <div className="brand">
          <BrandMark />
          <div>
            <strong>SteamNStats</strong>
            <span>Library value dashboard</span>
          </div>
        </div>
        <nav className="nav-list">
          <a className="nav-item active" href="#summary">
            <CircleDollarSign size={18} aria-hidden="true" /> Summary
          </a>
          <a className="nav-item" href="#library">
            <Gamepad2 size={18} aria-hidden="true" /> Library
          </a>
        </nav>
        <div className="sidebar-note">
          <ShieldCheck size={18} aria-hidden="true" />
          <span>Estimated value uses current Steam store prices, not purchase history.</span>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="profile">
            {user?.avatar_url ? <img src={user.avatar_url} alt="" /> : <div className="avatar-fallback" />}
            <div>
              <span className="muted-label">Signed in as</span>
              <strong>{user?.persona_name ?? user?.steam_id ?? "Steam user"}</strong>
            </div>
          </div>
          <div className="topbar-actions">
            <button className="button secondary" onClick={handleSync} disabled={isSyncing}>
              <RefreshCw size={17} className={isSyncing ? "spin" : ""} aria-hidden="true" />
              {isSyncing ? "Syncing library" : "Sync library"}
            </button>
            <button className="icon-button" onClick={handleLogout} aria-label="Log out">
              <LogOut size={18} aria-hidden="true" />
            </button>
          </div>
        </header>

        {error ? <div className="alert">{error}</div> : null}
        {state === "loading" ? <DashboardSkeleton /> : null}
        {state !== "loading" && summary ? (
          <>
            <section id="summary" className="summary-grid" aria-label="Library summary">
              <Metric
                icon={<CircleDollarSign size={20} aria-hidden="true" />}
                label="Estimated library value"
                value={formatMoney(summary.estimated_value_cents, summary.currency)}
                detail={`${summary.priced_games} priced, ${summary.unavailable_prices} unavailable`}
              />
              <Metric
                icon={<Gamepad2 size={20} aria-hidden="true" />}
                label="Owned games"
                value={summary.owned_games.toLocaleString()}
                detail={`${summary.free_games} free-to-play games`}
              />
              <Metric
                icon={<Clock3 size={20} aria-hidden="true" />}
                label="Total playtime"
                value={formatPlaytime(summary.total_playtime_minutes)}
                detail={`Last sync ${formatDateTime(summary.last_synced_at)}`}
              />
            </section>

            <section className="panel top-games">
              <div className="section-heading">
                <div>
                  <h2>Most played</h2>
                  <p>Sorted by lifetime playtime from your Steam library.</p>
                </div>
              </div>
              {summary.most_played.length > 0 ? (
                <div className="top-game-list">
                  {summary.most_played.map((game) => (
                    <div className="top-game" key={game.app_id}>
                      {game.header_image ? <img src={game.header_image} alt="" /> : <div />}
                      <span>{game.name}</span>
                      <strong>{formatPlaytime(game.playtime_forever_minutes)}</strong>
                    </div>
                  ))}
                </div>
              ) : (
                <EmptyState title="No playtime yet" action="Sync library" onAction={handleSync} />
              )}
            </section>

            <section id="library" className="panel library-panel">
              <div className="section-heading">
                <div>
                  <h2>Library</h2>
                  <p>Current store prices are cached and refreshed periodically.</p>
                </div>
                <label className="search-box">
                  <Search size={17} aria-hidden="true" />
                  <span className="sr-only">Search games</span>
                  <input
                    value={filter}
                    onChange={(event) => setFilter(event.target.value)}
                    placeholder="Search games"
                  />
                </label>
              </div>
              {filteredLibrary.length > 0 ? (
                <LibraryTable entries={filteredLibrary} />
              ) : (
                <EmptyState title="No games to show" action="Sync library" onAction={handleSync} />
              )}
            </section>
          </>
        ) : null}
      </main>
    </div>
  );
}

function LoginScreen() {
  return (
    <main className="login-screen">
      <section className="login-hero" aria-labelledby="login-title">
        <div className="login-copy">
          <BrandMark size="large" />
          <span className="login-kicker">SteamNStats library command</span>
          <h1 id="login-title">Your Steam library, priced and mapped.</h1>
          <p className="login-lede">
            Sign in once to turn owned games, playtime, and current Steam store prices into a
            private instrument panel for your collection. Every value stays labeled as an estimate.
          </p>

          <div className="login-command-card">
            <div className="login-command-status">
              <span>Private scan</span>
              <strong>OpenID verified, no Steam password shared</strong>
            </div>
            <a className="button primary login-cta" href={api.steamLoginUrl}>
              <ShieldCheck size={18} aria-hidden="true" />
              Sign in with Steam
            </a>
          </div>

          <div className="scan-pipeline" aria-label="What happens after sign in">
            <div className="scan-step active">
              <LibraryBig size={18} aria-hidden="true" />
              <strong>01</strong>
              <span>Import owned games</span>
            </div>
            <div className="scan-step">
              <Database size={18} aria-hidden="true" />
              <strong>02</strong>
              <span>Cache store prices</span>
            </div>
            <div className="scan-step">
              <BarChart3 size={18} aria-hidden="true" />
              <strong>03</strong>
              <span>Map value and playtime</span>
            </div>
          </div>
        </div>


        <aside className="login-preview demo-player" aria-label="Animated dashboard preview">
          <div className="demo-glow" aria-hidden="true" />
          <div className="demo-window-bar" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>

          <div className="demo-shell" aria-hidden="true">
            <div className="demo-rail">
              <BrandMark />
              <span className="rail-dot active" />
              <span className="rail-dot" />
              <span className="rail-dot" />
            </div>

            <div className="demo-content">
              <div className="preview-topline">
                <div>
                  <span>First sync preview</span>
                  <strong>Library instrument panel</strong>
                </div>
                <span className="sync-pill">Scanning prices</span>
              </div>

              <div className="preview-metrics">
                <div className="demo-focus-card">
                  <span>Estimated value</span>
                  <strong>$428.71</strong>
                </div>
                <div>
                  <span>Owned games</span>
                  <strong>146</strong>
                </div>
                <div>
                  <span>Playtime</span>
                  <strong>1,284h</strong>
                </div>
              </div>

              <div className="preview-chart">
                <span style={{ height: "42%" }} />
                <span style={{ height: "68%" }} />
                <span style={{ height: "53%" }} />
                <span style={{ height: "82%" }} />
                <span style={{ height: "61%" }} />
                <span style={{ height: "92%" }} />
                <span style={{ height: "74%" }} />
              </div>

              <div className="preview-list">
                <div className="preview-row row-playing">
                  <span className="game-strip blue" />
                  <div>
                    <strong>Most played game</strong>
                    <span>312 hours tracked</span>
                  </div>
                  <b>$19.99</b>
                </div>
                <div className="preview-row row-sale">
                  <span className="game-strip green" />
                  <div>
                    <strong>Best sale find</strong>
                    <span>75% off current price</span>
                  </div>
                  <b>$4.99</b>
                </div>
                <div className="preview-row row-cache">
                  <span className="game-strip slate" />
                  <div>
                    <strong>Needs a price</strong>
                    <span>Unavailable in store cache</span>
                  </div>
                  <b>Check</b>
                </div>
              </div>
            </div>
          </div>

          <div className="demo-popover demo-popover-sync" aria-hidden="true">
            <span>Refresh status</span>
            <strong>Store cache updated</strong>
          </div>
          <div className="demo-popover demo-popover-value" aria-hidden="true">
            <span>Estimate detail</span>
            <strong>142 priced games</strong>
          </div>
          <span className="demo-cursor" aria-hidden="true" />
        </aside>

      </section>
    </main>
  );
}

function BrandMark({ size = "default" }: { size?: "default" | "large" }) {
  return (
    <div className={`brand-mark ${size === "large" ? "large" : ""}`}>
      <img src={logoMark} alt="" />
    </div>
  );
}

function Metric({
  icon,
  label,
  value,
  detail
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <article className="metric-card">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}

function LibraryTable({ entries }: { entries: LibraryEntry[] }) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Game</th>
            <th>Playtime</th>
            <th>Current price</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.game.app_id}>
              <td>
                <div className="game-cell">
                  {entry.game.header_image ? <img src={entry.game.header_image} alt="" /> : <div />}
                  <span>{entry.game.name}</span>
                </div>
              </td>
              <td>{formatPlaytime(entry.playtime_forever_minutes)}</td>
              <td>
                <PriceBadge entry={entry} />
              </td>
              <td>{formatDateTime(entry.game.metadata_fetched_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PriceBadge({ entry }: { entry: LibraryEntry }) {
  if (entry.game.is_free) {
    return <span className="price-badge free">Free</span>;
  }

  if (entry.game.current_price_cents === null) {
    return <span className="price-badge unavailable">Unavailable</span>;
  }

  return (
    <span className="price-badge">
      {formatMoney(entry.game.current_price_cents, entry.game.currency)}
    </span>
  );
}

function EmptyState({
  title,
  action,
  onAction
}: {
  title: string;
  action: string;
  onAction: () => void;
}) {
  return (
    <div className="empty-state">
      <p>{title}</p>
      <button className="button secondary" onClick={onAction}>
        <RefreshCw size={17} aria-hidden="true" />
        {action}
      </button>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="skeleton-stack" aria-label="Loading dashboard">
      <div className="skeleton-row" />
      <div className="skeleton-row" />
      <div className="skeleton-row" />
    </div>
  );
}

function ShellSkeleton() {
  return <div className="page-skeleton" aria-label="Loading" />;
}
