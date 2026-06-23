import {
  Award,
  CheckCircle,
  ChevronDown,
  CircleDollarSign,
  Clock3,
  Gamepad2,
  Home,
  LibraryBig,
  LogOut,
  RefreshCw,
  Search,
  ShieldCheck,
  BarChart3,
  Database,
  ArrowRight
} from "lucide-react";
import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";
import { api, clearTokens, getAccessToken, getRefreshToken, setTokens } from "./api";
import logoMark from "./assets/steamnstats-logo.svg";
import { formatDateTime, formatMoney, formatPlaytime } from "./format";
import type { GenreStat, LibraryEntry, Summary, User } from "./types";

type LoadState = "idle" | "loading" | "loaded" | "error";

const SCREENS = ["home", "library"] as const;

const MOCK_GENRES: GenreStat[] = [
  { name: "RPG", count: 0 },
  { name: "Action", count: 0 },
  { name: "Adventure", count: 0 },
  { name: "Indie", count: 0 },
  { name: "Strategy", count: 0 }
];

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
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [activeScreen, setActiveScreen] = useState<"home" | "library">("home");
  const [navDirection, setNavDirection] = useState<1 | -1>(1);
  const mainRef = useRef<HTMLElement>(null);
  const activeScreenRef = useRef(activeScreen);
  activeScreenRef.current = activeScreen;

  function switchScreen(next: "home" | "library", direction: 1 | -1 = 1) {
    setNavDirection(direction);
    setActiveScreen(next);
  }

  useEffect(() => {
    const main = mainRef.current;
    if (!main) return;

    let cooldown = false;

    function onWheel(e: WheelEvent) {
      if (cooldown) return;

      const screens = main!.querySelectorAll(".screen");
      const screen = Array.from(screens).find(
        (el) => getComputedStyle(el).position !== "absolute"
      ) as HTMLElement | undefined;
      if (!screen) return;

      const canScrollDown = screen.scrollTop + screen.clientHeight < screen.scrollHeight - 1;
      const canScrollUp = screen.scrollTop > 0;

      if (e.deltaY > 0 && !canScrollDown) {
        const idx = SCREENS.indexOf(activeScreenRef.current);
        const nextIdx = (idx + 1) % SCREENS.length;
        switchScreen(SCREENS[nextIdx], 1);
        cooldown = true;
        setTimeout(() => { cooldown = false; }, 1000);
      } else if (e.deltaY < 0 && !canScrollUp) {
        const idx = SCREENS.indexOf(activeScreenRef.current);
        const prevIdx = (idx - 1 + SCREENS.length) % SCREENS.length;
        switchScreen(SCREENS[prevIdx], -1);
        cooldown = true;
        setTimeout(() => { cooldown = false; }, 1000);
      }
    }

    main.addEventListener("wheel", onWheel, { passive: true });
    return () => {
      main.removeEventListener("wheel", onWheel);
    };
  }, [callbackHandled, isAuthenticated]);

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
    setShowUserMenu(false);
  }

  function goToLibrary() {
    switchScreen("library");
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

  const topGame = summary?.most_played?.[0] ?? null;

  return (
    <div className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <div className="sidebar-logo">
          <BrandMark />
          <span className="sidebar-brand-text" title="SteamNStats">SNS</span>
        </div>

        <nav className="nav-list">
          <button
            className={`nav-item ${activeScreen === "home" ? "active" : ""}`}
            onClick={() => switchScreen("home")}
            aria-label="Home"
          >
            <Home size={20} aria-hidden="true" />
          </button>
          <button
            className={`nav-item ${activeScreen === "library" ? "active" : ""}`}
            onClick={() => switchScreen("library")}
            aria-label="Library"
          >
            <Gamepad2 size={20} aria-hidden="true" />
          </button>
        </nav>

        <div className="sidebar-footer">
          <div className="user-menu-container">
            <button
              className="user-avatar-button"
              onClick={() => setShowUserMenu(!showUserMenu)}
              aria-label="User menu"
            >
              {user?.avatar_url ? (
                <img src={user.avatar_url} alt="" className="user-avatar" />
              ) : (
                <div className="avatar-fallback" />
              )}
              <ChevronDown size={14} aria-hidden="true" />
            </button>
            {showUserMenu && (
              <div className="user-dropdown">
                <div className="user-dropdown-info">
                  <span className="muted-label">Signed in as</span>
                  <strong>{user?.persona_name ?? user?.steam_id ?? "Steam user"}</strong>
                </div>
                <button className="user-dropdown-item" onClick={handleLogout}>
                  <LogOut size={16} aria-hidden="true" />
                  Log out
                </button>
              </div>
            )}
          </div>
        </div>
      </aside>

      <main className="main" ref={mainRef}>
        <AnimatePresence mode="popLayout">
          {activeScreen === "home" ? (
            <motion.div
              key="home"
              className="screen"
              initial={{ opacity: 0, y: `${navDirection * 100}%` }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: `${navDirection * -100}%` }}
              transition={{ duration: 0.4, ease: [0.32, 0.72, 0, 1] }}
            >
              <section className="hero-section">
                <div className="hero-content">
                  <h1 className="hero-title">
                    Your games.<br />
                    <span className="hero-accent">Your world.</span>
                  </h1>
                  <p className="hero-subtitle">A lifetime of adventures, summarized.</p>
                </div>
                <div className="hero-actions">
                  <button className="button secondary" onClick={handleSync} disabled={isSyncing}>
                    <RefreshCw size={17} className={isSyncing ? "spin" : ""} aria-hidden="true" />
                    {isSyncing ? "Syncing" : "Sync"}
                  </button>
                </div>
              </section>

              {error ? <div className="alert">{error}</div> : null}
              {state === "loading" ? <DashboardSkeleton /> : null}
              {state !== "loading" && summary ? (
                <>
                  <section id="summary" className="stat-cards-row" aria-label="Library summary">
                    <StatCard
                      icon={<CircleDollarSign size={22} aria-hidden="true" />}
                      iconColor="green"
                      label="Estimated Value"
                      value={formatMoney(summary.estimated_value_cents, summary.currency)}
                    />
                    <StatCard
                      icon={<Clock3 size={22} aria-hidden="true" />}
                      iconColor="blue"
                      label="Hours Played"
                      value={formatPlaytime(summary.total_playtime_minutes)}
                    />
                    <StatCard
                      icon={<Gamepad2 size={22} aria-hidden="true" />}
                      iconColor="yellow"
                      label="Games Played"
                      value={summary.owned_games.toLocaleString()}
                    />
                    <StatCard
                      icon={<Award size={22} aria-hidden="true" />}
                      iconColor="gold"
                      label="Achievements"
                      value="—"
                      placeholder
                    />
                    <StatCard
                      icon={<CheckCircle size={22} aria-hidden="true" />}
                      iconColor="pink"
                      label="Games Completed"
                      value="—"
                      placeholder
                    />
                  </section>

                  <section className="bottom-section">
                    <MostPlayedCard game={topGame} onGoToLibrary={goToLibrary} />
                    <GameVarietyCard genres={MOCK_GENRES} totalGenres={0} />
                  </section>
                </>
              ) : null}
            </motion.div>
          ) : (
            <motion.div
              key="library"
              className="screen"
              initial={{ opacity: 0, y: `${navDirection * 100}%` }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: `${navDirection * -100}%` }}
              transition={{ duration: 0.4, ease: [0.32, 0.72, 0, 1] }}
            >
              {error ? <div className="alert">{error}</div> : null}
              {state === "loading" ? <DashboardSkeleton /> : null}
              {state !== "loading" ? (
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
              ) : null}
            </motion.div>
          )}
        </AnimatePresence>
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

function Sparkline({ color }: { color: string }) {
  const points = [4, 7, 5, 9, 6, 8, 3, 7, 10, 6, 8, 5];
  const width = 120;
  const height = 28;
  const maxVal = Math.max(...points);
  const minVal = Math.min(...points);
  const range = maxVal - minVal || 1;

  const coords = points.map((val, i) => {
    const x = (i / (points.length - 1)) * width;
    const y = height - ((val - minVal) / range) * (height - 4) - 2;
    return `${x},${y}`;
  });

  return (
    <svg className="sparkline" viewBox={`0 0 ${width} ${height}`} aria-hidden="true">
      <polyline
        points={coords.join(" ")}
        fill="none"
        stroke={color}
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

const SPARKLINE_COLORS: Record<string, string> = {
  green: "#a855f7",
  blue: "#60b1ff",
  yellow: "#4ade80",
  gold: "#f59e0b",
  pink: "#f472b6"
};

function StatCard({
  icon,
  iconColor,
  label,
  value,
  placeholder = false
}: {
  icon: React.ReactNode;
  iconColor: string;
  label: string;
  value: string;
  placeholder?: boolean;
}) {
  return (
    <article className={`stat-card ${placeholder ? "stat-card-placeholder" : ""}`}>
      <div className={`stat-icon stat-icon-${iconColor}`}>{icon}</div>
      <strong className="stat-value">{value}</strong>
      <span className="stat-label">{label}</span>
      <Sparkline color={SPARKLINE_COLORS[iconColor] ?? "#60b1ff"} />
    </article>
  );
}

function MostPlayedCard({
  game,
  onGoToLibrary
}: {
  game: { app_id: number; name: string; playtime_forever_minutes: number; header_image: string | null } | null;
  onGoToLibrary: () => void;
}) {
  return (
    <article className="most-played-card">
      <span className="card-label">Most Played Game</span>
      {game ? (
        <div className="most-played-content">
          <div className="most-played-info">
            <h3 className="most-played-name">{game.name}</h3>
            <div className="most-played-playtime">
              <Clock3 size={18} aria-hidden="true" />
              <strong>{formatPlaytime(game.playtime_forever_minutes)}</strong>
              <span>Hours Played</span>
            </div>
          </div>
          {game.header_image && (
            <img className="most-played-image" src={game.header_image} alt="" />
          )}
        </div>
      ) : (
        <p className="most-played-empty">No playtime data yet</p>
      )}
      <button className="go-to-library-btn" onClick={onGoToLibrary}>
        <LibraryBig size={18} aria-hidden="true" />
        Go to Library
        <ArrowRight size={16} aria-hidden="true" />
      </button>
    </article>
  );
}

function GameVarietyCard({
  genres,
  totalGenres
}: {
  genres: GenreStat[];
  totalGenres: number;
}) {
  const remaining = totalGenres > genres.length ? totalGenres - genres.length : 0;

  return (
    <article className="game-variety-card">
      <h3 className="card-label">Game Variety</h3>
      {totalGenres > 0 ? (
        <p className="variety-subtitle">
          You've explored <strong>{totalGenres}</strong> different genres
        </p>
      ) : (
        <p className="variety-subtitle">Genre data coming soon</p>
      )}
      <div className="genre-tags">
        {genres.map((g) => (
          <div className="genre-tag" key={g.name}>
            <span className="genre-name">{g.name}</span>
            <span className="genre-count">{g.count > 0 ? g.count : "—"}</span>
          </div>
        ))}
        {remaining > 0 && (
          <div className="genre-tag genre-tag-more">+ {remaining} more</div>
        )}
      </div>
      <div className="variety-decoration" aria-hidden="true">
        <Gamepad2 size={32} />
      </div>
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
