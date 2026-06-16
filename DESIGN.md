---
name: SteamNStats
description: Your Steam library, visualized.
colors:
  void-navy: "#0D1420"
  sidebar-navy: "#13263F"
  steam-blue: "#1E6EEB"
  chart-blue: "#60B1FF"
  slate: "#94A3B8"
  ice: "#E6EEF5"
  white: "#FFFFFF"
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
    backgroundColor: "{colors.steam-blue}"
    textColor: "{colors.white}"
    rounded: "{rounded.md}"
    padding: "0 14px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.chart-blue}"
    textColor: "{colors.void-navy}"
    rounded: "{rounded.md}"
  button-secondary:
    backgroundColor: "{colors.ice}"
    textColor: "{colors.void-navy}"
    rounded: "{rounded.md}"
    padding: "0 14px"
    height: "40px"
  panel:
    backgroundColor: "{colors.white}"
    textColor: "{colors.void-navy}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  logo-mark:
    backgroundColor: "{colors.void-navy}"
    textColor: "{colors.white}"
    rounded: "{rounded.icon}"
    size: "40px"
---

# Design System: SteamNStats

## 1. Overview

**Creative North Star: "The Library Instrument Panel"**

SteamNStats is a focused product dashboard for Steam players who want to understand library value, ownership, and playtime without theatrical gaming UI. The system should feel like a precise collector's instrument: dark navy where the interface needs structure, white or ice surfaces where the user needs to read, and electric blue only where interaction or data deserves attention.

The attached visual guide is the canonical brand direction. The old cobalt-and-copper system should be retired in favor of the SteamNStats palette, Poppins typography, and the Steam-inspired circular mark with ascending chart bars. Existing implementation tokens still use OKLCH and Inter in `frontend/src/styles.css`; future UI work should migrate those tokens to this guide while preserving the current product density.

**Key Characteristics:**
- Compact, repeat-visit dashboard layouts with dense but readable panels.
- A dark navy foundation balanced by clear white content surfaces.
- Electric blue for primary actions, active navigation, chart strokes, and selected states.
- Honest estimate language: values are current-price estimates, never purchase receipts.
- A real logo mark replaces the temporary `SN` square wherever brand identity appears.

## 2. Colors

The palette is a restrained Steam-native system: deep navy for trust, bright blue for action and value visualization, slate for quiet metadata, and ice for neutral surface separation.

### Primary
- **Void Navy** (`#0D1420`): The core identity color. Use for logo fills, dark sidebar sections, dense header bands, and high-emphasis text on light backgrounds.
- **Steam Blue** (`#1E6EEB`): The main action and selection color. Use for primary buttons, active navigation, interactive chart lines, and high-confidence positive data.
- **Chart Blue** (`#60B1FF`): The lighter data-viz blue. Use for bar-chart gradients, line-chart highlights, hover accents, and focus rings when paired with navy.

### Secondary
- **Sidebar Navy** (`#13263F`): The structural dark surface for sidebars, top bars, and dark panels. Use when `#0D1420` would feel too heavy across a large area.

### Neutral
- **Slate** (`#94A3B8`): Metadata, labels, secondary text, disabled icon color, and low-priority chart annotations.
- **Ice** (`#E6EEF5`): Page wash, skeleton shimmer base, subtle input fills, and dividers on white surfaces.
- **White** (`#FFFFFF`): Primary reading surface and logo negative space.

### Named Rules

**The Blue Earns Its Place Rule.** Steam Blue and Chart Blue are functional colors, not decoration. If an element is not clickable, selected, focused, or carrying data, it should usually stay navy, slate, white, or ice.

**The Dark Surface Rule.** Dark navy is for navigation, identity, or dense status panels. Long-form tables and repeated rows remain light for scan speed.

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

SteamNStats should be flat-by-default. Depth comes from tonal layering, borders, and state changes rather than ambient drop shadows. The current UI already follows this direction with bordered panels and a focus ring; keep that discipline as the brand moves darker.

### Shadow Vocabulary
- **Focus Ring** (`0 0 0 3px rgba(96, 177, 255, 0.45)`): Keyboard focus on buttons, links, search inputs, and icon buttons.
- **Interactive Lift** (`0 4px 8px rgba(13, 20, 32, 0.12)`): Optional hover treatment for dark icon tiles or logo cards only. Do not pair this with decorative wide shadows.

### Named Rules

**The No Ghost Cards Rule.** Avoid soft decorative shadows on bordered dashboard panels. Use one clear border, tonal contrast, or an interactive state.

## 5. Components

The component system is practical and familiar. Controls should feel like a serious dashboard with a gaming-library identity, not a storefront skin.

### Logo
- **Asset:** Use [frontend/src/assets/steamnstats-logo.svg](/Users/leonardo.murakami/Personal/IME/steamnstats/frontend/src/assets/steamnstats-logo.svg) for the mark.
- **Shape:** Circular navy mark with a white Steam-arm motif and ascending blue chart bars.
- **Clear Space:** Keep at least one `N`-width of space around the lockup, using the height of the `N` in `SteamNStats` as the unit.
- **Lockups:** Horizontal is default in the sidebar and login panel; stacked is allowed for centered empty states; icon-only is allowed for favicons, compact nav, and app tiles.

### Buttons
- **Shape:** Compact rectangle with 8px radius.
- **Primary:** Steam Blue background, white text, 40px height, 14px horizontal padding, icon before label when the action benefits from recognition.
- **Hover / Focus:** Hover may brighten toward Chart Blue; keyboard focus uses the focus ring from Elevation.
- **Secondary / Ghost:** Ice fill or transparent background with Void Navy text. Keep inactive states muted, not saturated.

### Cards / Containers
- **Corner Style:** 10px radius for panels, 8px for metric and table containers.
- **Background:** White for data panels; Ice for page wash and skeletons; Sidebar Navy or Void Navy for navigation and brand bands.
- **Shadow Strategy:** Flat by default. Use borders and tonal contrast before shadow.
- **Border:** 1px solid Ice on light surfaces or a low-alpha white stroke on dark navy.
- **Internal Padding:** 18px for panels, 14px for compact controls, 24px for major page gutters.

### Inputs / Fields
- **Style:** White or Ice fill, 1px Ice border, 8px radius, 40px minimum height.
- **Focus:** Border shifts to Chart Blue and receives the shared focus ring.
- **Placeholder:** Slate at full opacity so placeholder text remains readable.
- **Error / Disabled:** Error uses a distinct red state with text and icon support; disabled states lower opacity and keep cursor feedback clear.

### Navigation
- **Sidebar:** Sidebar Navy or Ice depending on surface context. Use the full logo lockup at the top and reserve active blue for the current destination.
- **Nav Items:** 40px minimum height, 8px radius, icon plus label, active state with Steam Blue text and a subtle blue-tinted fill.
- **Top Bar:** Light, utilitarian, and compact. User identity and sync status stay visible on repeat visits.

### Data Visualization
- **Charts:** Blue gradients may run from Steam Blue to Chart Blue. Bars should be rectangular with modest rounding, never ornamental.
- **Tables:** Dense rows, sticky headers on wide screens, card-like rows on narrow screens.
- **Metrics:** Large tabular numerals, concise labels, and detail copy that names uncertainty or cache age when relevant.

## 6. Do's and Don'ts

**Do:**
- Use the guide palette exactly for brand-critical surfaces.
- Keep the dashboard dense, calm, and task-first.
- Prefer borders, fills, and contrast over decorative shadow.
- Use the logo SVG in place of the temporary `SN` mark.
- Label estimated value as an estimate anywhere it appears.
- Preserve reduced-motion behavior for shimmer, spin, hover, and refresh feedback.

**Don't:**
- Reintroduce the copper accent from the previous design direction.
- Use noisy neon gaming treatments, decorative chart flourishes, or storefront-style promotion.
- Use gradient text, oversized metric gimmicks, or ornamental cards.
- Put full-saturation blue on inactive states.
- Let the dark brand palette reduce table readability.
- Treat current Steam store price as exact historical spend.
