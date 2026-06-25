---
name: SteamNStats
description: Your Steam library, visualized.
colors:
  void-navy: "#0a0e1a"
  sidebar-navy: "#0f1629"
  primary-purple: "#7c3aed"
  accent-purple: "#a78bfa"
  slate: "#94A3B8"
  ice: "#E6EEF5"
  white: "#FFFFFF"
  surface: "rgba(255, 255, 255, 0.04)"
  border: "rgba(255, 255, 255, 0.08)"
typography:
  display:
    fontFamily: "Poppins, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "3.2rem"
    fontWeight: 600
    lineHeight: 0.98
    letterSpacing: "0"
  headline:
    fontFamily: "Poppins, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.65rem"
    fontWeight: 600
    lineHeight: 1.15
    letterSpacing: "0"
  title:
    fontFamily: "Poppins, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "0"
  body:
    fontFamily: "Poppins, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 400
    lineHeight: 1.55
    letterSpacing: "0"
  label:
    fontFamily: "Poppins, Inter, ui-sans-serif, system-ui, sans-serif"
    fontSize: "0.82rem"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.08em"
rounded:
  sm: "6px"
  md: "8px"
  lg: "10px"
  icon: "14px"
spacing:
  xs: "6px"
  sm: "8px"
  md: "14px"
  lg: "18px"
  xl: "24px"
components:
  button-primary:
    backgroundColor: "{colors.primary-purple}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: "0 14px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.accent-purple}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ice}"
    rounded: "{rounded.md}"
    padding: "0 14px"
    height: "40px"
  panel:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ice}"
    rounded: "12px"
    padding: "22px"
  stat-card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ice}"
    rounded: "12px"
    padding: "18px"
  logo-mark:
    backgroundColor: "{colors.sidebar-navy}"
    textColor: "{colors.white}"
    rounded: "{rounded.icon}"
    size: "40px"
---

# Design System: SteamNStats

## 1. Overview

**Creative North Star: "The Gaming Command Center"**

SteamNStats is a full-dark dashboard for Steam players. The interface is built entirely on deep navy surfaces with glass-like translucent cards, purple accents for interaction and data highlights, and a narrow icon-only sidebar. The design favors a modern, minimalist aesthetic with generous spacing and subtle gradient glows.

**Key Characteristics:**
- Full dark theme: deep navy background (#0a0e1a) with translucent glass card surfaces.
- Narrow icon-only sidebar (72px) for navigation; main content fills remaining space.
- Hero headline section with "Your games. Your world." and subtle radial gradient glow.
- Five stat cards in a horizontal row with colored icon circles and sparkline charts.
- Bottom section with featured "Most Played Game" card and "Game Variety" genre card.
- Purple (#7c3aed / #a78bfa) replaces blue as the primary action and accent color.
- Honest estimate language: values are current-price estimates, never purchase receipts.
- Logo mark in sidebar with brand text below.

## 2. Colors

The palette is a deep-dark system built for immersive dashboard use: navy backgrounds, purple accents, and muted slate for secondary text.

### Primary
- **Void Navy** (`#0a0e1a`): The page background. Deep, near-black navy.
- **Primary Purple** (`#7c3aed`): Buttons, active nav highlights, CTA elements, and interactive chart accents.
- **Accent Purple** (`#a78bfa`): Hover states, hero accent text, sparkline highlights, and lighter interactive touches.

### Secondary
- **Sidebar Navy** (`#0f1629`): Sidebar background. Slightly lighter than void navy.
- **Surface** (`rgba(255,255,255,0.04)`): Glass-like card backgrounds. Translucent white over navy.
- **Surface Solid** (`#111827`): Dropdown menus and overlays needing opaque backgrounds.

### Neutral
- **Slate** (`#94A3B8`): Labels, secondary text, muted icons, and metadata.
- **Ice** (`#E6EEF5`): Primary text color on dark backgrounds.
- **White** (`#FFFFFF`): Logo negative space and high-emphasis login text.

### Stat Card Icon Colors
- **Green** (`#4ade80`): Estimated Value icon circle.
- **Blue** (`#60b1ff`): Hours Played icon circle.
- **Gold** (`#f59e0b`): Achievements icon circle.
- **Pink** (`#f472b6`): Games Completed icon circle.

### Named Rules

**The Purple Earns Its Place Rule.** Purple is functional, not decorative. Use it only for clickable, selected, focused, or data-carrying elements.

**The Full-Dark Rule.** The entire dashboard is dark. Cards use translucent glass surfaces. There are no white content areas in the authenticated view.

## 3. Typography

**Display Font:** Poppins SemiBold, with Inter and system sans fallbacks.
**Body Font:** Poppins Regular, with Inter and system sans fallbacks.
**Label/Mono Font:** Poppins SemiBold for labels; tabular numerals enabled for values.

**Character:** Poppins gives the product a clean geometric voice that matches the guide without feeling like a marketing page. The dashboard should use Poppins with modest sizes, compact line heights, and strong weight contrast rather than oversized headings.

### Hierarchy
- **Display** (600, `3.2rem`, `0.98`): Login and empty-state headline moments only. Keep line length short and use `text-wrap: balance`.
- **Headline** (600, `1.65rem`, `1.15`): Primary metric values and major dashboard figures. Always use tabular numerals for values.
- **Title** (600, `1.1rem`, `1.25`): Panel headings, top-game names, and section titles.
- **Body** (400, `0.95rem`, `1.55`): Interface copy, explanatory text, and table content. Cap prose around 65-75ch.
- **Label** (600, `0.82rem`, `0.08em` only for short labels): Metadata labels, table headers, and short brand-system captions. Do not use all-caps sentence copy.

### Named Rules

**The Product Scale Rule.** Product screens use fixed rem sizes, not fluid type. The logo lockup may be larger in brand assets, but the authenticated dashboard stays compact.

## 4. Elevation

SteamNStats is flat-by-default. Depth comes from translucent layering, subtle border contrast, and radial gradient glows rather than drop shadows.

### Shadow Vocabulary
- **Focus Ring** (`0 0 0 3px rgba(124, 58, 237, 0.45)`): Keyboard focus on buttons, links, search inputs, and icon buttons. Purple-tinted.
- **Hero Glow**: Radial gradient (`rgba(124,58,237,0.12)`) positioned in the upper-right area of the hero section. Decorative ambient light.

### Named Rules

**The No Ghost Cards Rule.** Avoid soft decorative shadows on bordered dashboard panels. Use one clear border, tonal contrast, or an interactive state.

## 5. Components

The component system is modern and immersive. Controls should feel like a polished gaming dashboard.

### Logo
- **Asset:** `frontend/src/assets/steamnstats-logo.svg`
- **Placement:** Centered in the 72px icon sidebar with brand text below.
- **Lockups:** Icon-only in the sidebar; large mark on login screen.

### Buttons
- **Shape:** Compact rectangle with 8px radius.
- **Primary:** Purple background, white text, 40px height, 14px horizontal padding.
- **Hover / Focus:** Hover brightens to accent purple; keyboard focus uses the purple focus ring.
- **Secondary / Ghost:** Translucent surface background with light text. Border is low-alpha white.
- **Go to Library:** Full-width purple button with icon and arrow, 10px radius.

### Cards / Containers
- **Corner Style:** 12px radius for all cards and panels.
- **Background:** Translucent glass (`rgba(255,255,255,0.04)`) for cards on dark backgrounds.
- **Border:** `1px solid rgba(255,255,255,0.08)` on all card edges.
- **Internal Padding:** 18-22px for cards, 32px for main content gutters.

### Stat Cards
- **Layout:** 5 cards in a horizontal row (3 real data + 2 placeholder).
- **Structure:** Colored icon circle (40px round), large value, muted label, sparkline SVG.
- **Placeholder cards:** Reduced opacity (0.55), value shows "—".
- **Sparklines:** SVG `<polyline>`, colored per card. Show mock data as placeholder; real sync history data when available.

### Inputs / Fields
- **Style:** Translucent surface fill, low-alpha white border, 8px radius, 40px minimum height.
- **Focus:** Border brightens and receives the purple focus ring.
- **Placeholder:** Slate at full opacity.

### Navigation
- **Sidebar:** 72px wide, icon-only, centered vertically. Sidebar Navy background.
- **Nav Items:** 44px square, 12px radius, icon only, active state with purple-tinted fill.
- **User Menu:** Avatar + chevron in hero section top-right, dropdown on click.

### Data Visualization
- **Sparklines:** Per-card SVG polyline charts with card-specific colors.
- **Tables:** Dark-themed with translucent hover rows. Dense layout.
- **Metrics:** Large tabular numerals with variant-numeric: tabular-nums.

### Bottom Section
- **Layout:** Two-column grid below stat cards.
- **Most Played Card:** Game name, playtime with clock icon, header image from API, "Go to Library" CTA button.
- **Game Variety Card:** Genre tag pills, count badges, decorative bubble visualization.

## 6. Do's and Don'ts

**Do:**
- Use the full-dark palette consistently across the authenticated dashboard.
- Keep the icon sidebar narrow (72px) and navigation minimal.
- Use translucent glass cards on the dark background.
- Use purple only for interactive and data-carrying elements.
- Label estimated value as an estimate anywhere it appears.
- Show sparklines only when meaningful historical data is available.
- Preserve reduced-motion behavior for shimmer, spin, hover, and refresh feedback.

**Don't:**
- Introduce white content surfaces in the authenticated view.
- Use noisy neon gaming treatments or storefront-style promotion.
- Use gradient text or oversized metric gimmicks.
- Put full-saturation purple on inactive states.
- Treat current Steam store price as exact historical spend.
- Add text labels to sidebar nav items in the desktop layout.
