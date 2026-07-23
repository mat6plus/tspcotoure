# TSP Couture — Digital Showroom

> **Pure vanilla HTML/JS + Tailwind CDN.** No build step, no package manager, no server required.  
> Open `index.html` directly in any modern browser to run the full site locally.

---

## Project Structure

```
rom_couture_final/
├── index.html          ← Home page (hero, testimonials, feature grid, lookbook)
├── gallery.html        ← Masonry lookbook with category filters → order handoff
├── custom-order.html   ← 5-step bespoke order wizard (fabric swatches, dropzone)
├── how-it-works.html   ← 3-phase artisan journey timeline
├── about.html          ← Brand story, atelier values, trust badges
├── styles.css          ← Consolidated custom styles (loaded via shared.js)
├── security.js         ← Client-side validation & XSS sanitization utilities
├── shared.js           ← Unified nav, policy ribbon & footer injection
└── README.md           ← This file
```

---

## How to Run Locally

### Option A — Double-click (simplest)
1. Open Finder and navigate to `rom_couture_final/`
2. Double-click `index.html`
3. It opens in your default browser at a `file://` URL

> **Note:** All inter-page links are relative (e.g. `gallery.html`, `custom-order.html`), so navigation works correctly from any `file://` path as long as all files stay in the same folder.

### Option B — Local HTTP server (recommended for full feature parity)

Some browsers restrict certain APIs on `file://` URLs. Use a tiny local server to avoid this:

**With Python 3 (pre-installed on macOS):**
```bash
cd /Users/mac/Desktop/rom_couture_main/rom_couture_final
python3 -m http.server 8001
```
Then open: **http://localhost:8001**

**With Node.js (`npx`):**
```bash
cd /Users/mac/Desktop/rom_couture_main/rom_couture_final
npx -y serve .
```
Then open the URL printed in the terminal (usually **http://localhost:3000**).

---

## Technology Stack

| Layer | Technology | Notes |
|---|---|---|
| Structure | HTML5 (semantic) | No frameworks |
| Styling | Tailwind CSS CDN + `styles.css` | Custom terracotta theme via `tailwind.config` |
| Typography | Google Fonts | Playfair Display · Inter · Space Grotesk |
| Icons | Material Symbols Outlined | Variable font, weight 200 |
| Interactivity | Vanilla JavaScript (ES2020) | IntersectionObserver, drag-and-drop, carousel |
| Security | `security.js` namespace | XSS sanitization, email/phone/measurement validation |
| Shared UI | `shared.js` injection | Nav, policy ribbon, footer — single source of truth |

---

## Page-by-Page Notes

### `index.html` — Home
- **LCP image** loaded with `fetchpriority="high"` for best Core Web Vitals score
- Auto-advancing testimonial carousel (6 s interval, pauses on hover)
- `.reveal-on-scroll` stagger via `IntersectionObserver` on feature cards and lookbook grid

### `gallery.html` — Lookbook
- Category filter buttons toggle `.hidden` on masonry cards
- "Start Design" arrow buttons pass the garment name to `custom-order.html` via URL param:  
  `custom-order.html?garment=Ankara+Blazer`
- The custom-order page reads `URLSearchParams` on load and pre-selects the matching garment radio

### `custom-order.html` — 5-Step Order Wizard
- **Step 1** — Garment type (pre-filled from gallery `?garment=` param)
- **Step 2** — Fabric swatch selector (interactive, single-select)
- **Step 3** — Design details (Pinterest URL, notes textarea)
- **Step 4** — Measurements (12 numeric fields with boundary validation via `security.js`)
- **Step 5** — Contact + sketch upload (drag-and-drop, 10 MB max, JPG/PNG/WEBP only)
- Full `SecurityUtils` validation: email regex, international phone regex, measurement range guards
- ⚠️ **Server-side validation is required before any production deployment.** Client-side checks are UX guards only.

### `how-it-works.html` — Process Timeline
- 3-phase alternating layout (image left/right) with vertical connector line
- Desktop step-circle nodes scale + pulse on `group-hover`
- Each `section` triggers `.reveal-on-scroll → .active` at 5% viewport intersection

### `about.html` — Brand Story
- Full-bleed hero with parallax-style image
- Blockquote pull-quote and two-column narrative
- Four atelier-values icon cards with staggered scroll reveal
- Social proof stat bar + ethics / no-returns explainer

---

## Shared Components

### `security.js` — `window.SecurityUtils`
Must be loaded **before** `shared.js`.

| Method | Purpose |
|---|---|
| `sanitizeInput(str)` | Strips dangerous HTML characters |
| `encodeHTML(str)` | HTML-encodes for safe DOM insertion |
| `safeRender(el, text)` | Sets `textContent` (never `innerHTML`) |
| `validateEmail(str)` | RFC-compliant email regex |
| `validatePhone(str)` | International phone number regex |
| `validateMeasurement(val, min, max)` | Numeric range boundary check |
| `validateFileUpload(file)` | 10 MB limit, JPG/PNG/WEBP only |

### `shared.js` — Dynamic Injection
Runs on `DOMContentLoaded`. Looks for empty `<nav>` and `<footer>` placeholder tags and fills them.

- Detects `window.location.pathname` to highlight the active nav link
- Injects `#security-ribbon` (policy bar) immediately after `<nav>`
- Sets up mobile drawer toggle with keyboard (`Escape`) and outside-click dismissal
- Newsletter form uses `SecurityUtils.validateEmail` before mock-submission

---

## Customisation

### Colour Palette
All colours are defined in the `tailwind.config` block at the top of each HTML file.  
The primary terracotta is `#914325`. To rebrand, update `"primary": "#914325"` in each page's config block and `security.js`/`shared.js` are colour-agnostic.

### Adding a New Page
1. Copy the `<head>` block (including Tailwind CDN, fonts, and `tailwind.config` script) from any existing page
2. Add an empty `<nav></nav>` at the top of `<body>` and an empty `<footer></footer>` before closing `</body>`
3. Load `security.js` then `shared.js` at the bottom of `<body>` — in that order
4. Add your page's filename to the nav links array in `shared.js` `injectNavBar()`

---

## Browser Support

| Browser | Minimum Version |
|---|---|
| Chrome / Edge | 88+ |
| Firefox | 85+ |
| Safari | 14+ |

Features used: CSS custom properties, `IntersectionObserver`, `URLSearchParams`, CSS Grid, `backdrop-filter`, `aspect-ratio`.

---

## Security Notes

> ⚠️ This is a **static client-side prototype**. Before any production deployment:
> - Implement server-side form validation and sanitization
> - Move newsletter subscriptions to a real backend (e.g. Mailchimp API, Firebase Functions)
> - Add CSRF protection and rate-limiting on any backend endpoints
> - Replace `console.log` submission stubs with real API calls

---

*© 2026 TSP Couture. Digital Craftsmanship for the Modern Artisan.*
