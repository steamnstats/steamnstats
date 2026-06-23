# Product

## Register

product

## Users

Steam players who want a clear account-level view of their library value,
playtime, and owned game metadata. They use the product as a personal dashboard
after signing in with Steam.

## Product Purpose

SteamNStats aggregates Steam profile, library, and store metadata so users can
estimate the current value of their owned library and understand their playtime
patterns without repeatedly fetching the same external data.

## Brand Personality

Precise, candid, collector-minded. The product should feel trustworthy and
calm, with enough visual character to fit a gaming library tool without turning
into a storefront.

## Anti-references

Do not imitate SteamDB data access patterns, scrape protected pages, or present
estimated value as exact purchase spend. Visually, avoid landing-page hero
flourish, noisy gaming neon, decorative charts, and oversized metric gimmicks.

## Dashboard Layout

The authenticated dashboard uses a full-dark theme with:
- A narrow icon-only sidebar (72px) on the left with logo and navigation.
- A hero section with the headline "Your games. Your world." and user avatar.
- Five stat cards in a row: Estimated Value, Hours Played, Games Played,
  Achievements (placeholder), and Games Completed (placeholder).
- A bottom section with a featured "Most Played Game" card and a "Game Variety"
  genre distribution card (placeholder).
- A full library table below with search, current prices, and playtime data.

## Design Principles

- Label estimates honestly and keep uncertainty visible.
- Put library scanning, comparison, and refresh status ahead of promotion.
- Use the full-dark theme with translucent glass cards for an immersive feel.
- Keep external data failures understandable and recoverable.
- Treat cached data age as part of the interface, not an implementation detail.
- Show sparklines only when enough historical sync data points are available.

## Accessibility & Inclusion

Target WCAG AA contrast. Support keyboard navigation, visible focus states,
reduced motion preferences, and color-blind-safe status distinctions that do
not rely on color alone.
