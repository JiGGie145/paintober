# Plan: Paintober Vue 3 Frontend

## Stack
- Vue 3 + Vite, JavaScript (no TypeScript)
- Vanilla CSS / CSS Modules
- Vue Router 4, Pinia
- Separate dev server (localhost:5173); Vite proxy eliminates CORS need
- Google Fonts: Raleway (headers) + Urbanist (body)

## Design System: "Gen-Z Digital Scrapbook"
All tokens live in `src/assets/theme.css` as CSS custom properties. No component hard-codes colors, font sizes, spacing, or shadows.

### Palette
| Token | Value | Use |
|---|---|---|
| `--color-bg` | `#1B1C1E` | App background |
| `--color-lime` | `#CFFF04` | Primary CTA, active states |
| `--color-indigo` | `#8D7EFF` | Headers, nav containers |
| `--color-lavender` | `#B87EEE` | Secondary buttons, in-progress |
| `--color-snow` | `#EDEBEE` | Card backgrounds, text on dark |
| `--color-midnight` | `#0B4550` | Hard shadows, icon fills |
| `--color-pink` | `#FF6B9D` | Decorative blobs only |

### Sticker Rules (applied globally via theme.css)
- `--border-sticker`: `3px solid` (min 2px — sticker outline feel)
- `--shadow-sticker-sm`: `3px 3px 0px 0px var(--color-midnight)` — zero blur, hard offset
- `--shadow-sticker-md`: `4px 4px 0px 0px var(--color-midnight)`
- `--shadow-sticker-lg`: `6px 6px 0px 0px var(--color-midnight)`
- `--radius-card`: `20px`; `--radius-badge`: `12px`; `--radius-circle`: `50%`
- Slight rotation on cards: `rotate(-2deg)`, `rotate(1deg)` per scrapbook aesthetic

### Typography tokens
- `--font-display`: `'Raleway', sans-serif` — used for all headings and CTAs
- `--font-body`: `'Urbanist', sans-serif` — all body/UI text and paint numbers
- `--text-hero`: `3rem / 800`; `--text-heading`: `2.5rem / 800`; `--text-subheading`: `1.5rem / 700`; `--text-body`: `1.125rem / 500`; `--text-sm`: `0.875rem / 700`

### Spacing tokens
- `--space-xs`: `4px`; `--space-sm`: `8px`; `--space-md`: `16px`; `--space-lg`: `24px`; `--space-xl`: `48px`; `--space-2xl`: `80px`

---

## Project Root
`paintober_frontend/` — scaffold new Vite project here

## Directory Structure
```
paintober_frontend/
├── index.html
├── vite.config.js
├── package.json
└── src/
    ├── main.js
    ├── App.vue
    ├── assets/
    │   ├── theme.css          ← SINGLE SOURCE OF TRUTH for all tokens
    │   └── main.css           ← global reset; imports theme.css + Google Fonts
    ├── api/
    │   └── jobs.js            ← JWT/CSRF-aware fetch wrapper + all API calls
    ├── components/
    │   ├── hero/
    │   │   ├── HeroSection.vue    ← position:relative container, composes layers
    │   │   ├── HeroBackground.vue ← position:absolute, z-index:0; blobs/shapes/anims only
    │   │   └── HeroContent.vue    ← position:relative, z-index:1; text + CTA only
    │   ├── studio/
    │   │   ├── FileDropzone.vue
    │   │   ├── UploadPanel.vue
    │   │   ├── ParametersPanel.vue
    │   │   ├── BasicParams.vue
    │   │   ├── ByopSection.vue
    │   │   ├── ProcessingScreen.vue
    │   │   └── ResultsScreen.vue
    │   └── shared/
    │       ├── AppHeader.vue
    │       ├── AppFooter.vue
    │       ├── ErrorBanner.vue
    │       └── HistoryPanel.vue
    ├── composables/
    │   ├── useJobPoller.js
    │   └── useFileUpload.js
    ├── stores/
    │   ├── jobStore.js
    │   └── historyStore.js
    └── views/
        ├── HomeView.vue       ← landing: hero + how-it-works + for-hosts + cta
        └── StudioView.vue     ← upload → configure → processing → results
```

---

## Phases

### ✅ Phase 1 — Scaffold & Theme System (COMPLETED)
1. ✅ `npm create vite@latest paintober_frontend -- --template vue` from project root
2. ✅ Install `vue-router@4`, `pinia`
3. ✅ Configure `vite.config.js` proxy: `/api/*` → `http://localhost:8000` (no CORS needed)
4. ✅ Add Google Fonts `<link>` in `index.html`: Raleway (weights 700, 800, 900) + Urbanist (weights 400, 500, 700)
5. ✅ Create `src/assets/theme.css`: all CSS custom properties — palette, sticker border/shadow tokens, typography tokens, spacing tokens, and the `@keyframes float` animation
6. ✅ Create `src/assets/main.css`: CSS reset, `body { background: var(--color-bg); font-family: var(--font-body); color: var(--color-snow); }`, imports theme.css
7. ✅ **No component may hard-code a color, font size, spacing value, or shadow** — all reference theme tokens

### ✅ Phase 2 — API Layer & State (COMPLETED)

8. ✅ `src/api/jobs.js`: JWT/CSRF-aware fetch wrapper — sends a bearer token for organizer requests, reads `csrftoken` from `document.cookie` for session-backed unsafe requests, always includes `credentials: 'include'`; exports `createJob(formData)`, `getJob(jobId)`, `listJobs()`
9. ✅ `src/stores/jobStore.js` (Pinia): `id`, `status`, `downloadUrls`, `error`, `parameters`; `reset()` action
10. ✅ `src/stores/historyStore.js` (Pinia): `jobs[]`, `fetchHistory()` action
11. ✅ `src/composables/useJobPoller.js`: `setInterval` every 5s → `getJob()` → updates jobStore; clears on `done`/`failed`/`onUnmounted`
12. ✅ `src/composables/useFileUpload.js`: drag-and-drop events + file-picker; client-side validation (format: JPG/JPEG/PNG/WEBP, size ≤50 MB)

### ✅ Phase 3 — Routing & App Shell (COMPLETED)

13. ✅ Vue Router: `/` → `HomeView`, `/studio` → `StudioView`
14. ✅ `App.vue`: `AppHeader` + `<router-view>` + `AppFooter`; background is `var(--color-bg)` from body, no further wrapper styling
15. ✅ `AppHeader.vue`: logo badge styled with `var(--color-indigo)` background + `var(--shadow-sticker-md)` + clip-path octagon corners (matches design); "Start Creating" nav link; history panel toggle button

### ✅ Phase 4 — Hero Section (Landing Page) (COMPLETED)

16. ✅ **`HeroSection.vue`**: `position: relative; overflow: hidden; min-height: 100vh` — only structural, no decorative rules
17. ✅ **`HeroBackground.vue`**: `position: absolute; inset: 0; z-index: 0; pointer-events: none`
    - Lime circle blob (top-left, `var(--color-lime)`, border `var(--border-sticker)` snow, `var(--shadow-sticker-sm)` midnight, `border-radius: 50%`, `animation: float 6s ease-in-out infinite`)
    - Pink rotated square (top-right, `var(--color-pink)`, `transform: rotate(45deg)`, `animation: float 8s ease-in-out 1s infinite`)
    - Indigo star blob (bottom-left, `var(--color-indigo)`, `clip-path: polygon(50% 0%, 61% 35%, 98% 35%, 68% 57%, 79% 91%, 50% 70%, 21% 91%, 32% 57%, 2% 35%, 39% 35%)`, `animation: float 7s ease-in-out 2s infinite`)
    - Float keyframes defined in `theme.css`: `0%/100% translateY(0)`, `50% translateY(-20px)`
    - **Zero text. Zero layout logic.**
18. ✅ **`HeroContent.vue`**: `position: relative; z-index: 1` — **zero background styling, zero decorative absolute elements**
    - Logo badge: `clip-path` octagon shape, `var(--color-indigo)` bg, `var(--color-snow)` border, `var(--shadow-sticker-lg)` midnight; "PAINTOBER" in `var(--font-display)` weight 900
    - H2 headline: `var(--font-display)` 800, `var(--color-snow)`, `text-shadow: 3px 3px 0 var(--color-midnight)`; `<span>` for "Paint-by-Numbers" colored `var(--color-lime)`
    - Subtext paragraph: `var(--font-body)` 500, `var(--color-snow)`
    - CTA button: `var(--color-lime)` bg, `4px solid var(--color-bg)` border, `var(--shadow-sticker-lg)`, `var(--radius-card)`, `var(--font-display)` 800, `color: var(--color-bg)`; hover `scale(1.05)`, active `scale(0.95)`; `router-link` to `/studio`
    - Before/After mockup cards: two rotated sticker cards (`rotate(-3deg)` / `rotate(2deg)`), "BEFORE" and "AFTER" badge labels; purely illustrative/static
19. ✅ `HomeView.vue`: `HeroSection` + How It Works section (3 rotated sticker cards, step numbers as `var(--color-indigo)`/`var(--color-lavender)`/`var(--color-lime)` circles) + "Perfect for Event Hosts" section (`var(--color-midnight)` bg, feature tag cards) + final CTA section

### ✅ Phase 5 — Studio: Upload & Configure (COMPLETED)

20. ✅ `StudioView.vue`: conditional rendering based on `jobStore.status` — `null` → `UploadPanel`, `pending/processing` → `ProcessingScreen`, `done` → `ResultsScreen`, `failed` → error in `ErrorBanner` + return to `UploadPanel`
21. ✅ `FileDropzone.vue`: drag-and-drop zone styled as a large sticker card — dashed border `var(--border-sticker)` `var(--color-indigo)`, `var(--shadow-sticker-md)`; active drag state swaps border to `var(--color-lime)`; "Upload" icon in lime
22. ✅ `UploadPanel.vue`: wraps `FileDropzone`; shows selected file name + size; format/size error via `ErrorBanner`; "Continue" button (lime sticker style) only enabled when valid file selected
23. ✅ `ParametersPanel.vue`: collapsible accordion card (`var(--color-snow)` bg, `var(--shadow-sticker-md)`); collapsed by default; delegates to `BasicParams` and `ByopSection`
24. ✅ `BasicParams.vue`: range inputs for `k_colors` (2–32, default 12), `line_thickness` (1–10), `min_region_area`, `min_label_spacing`; checkbox for `apply_gaussian`; number input for `contour_epsilon`; all labels in `var(--font-body)`
25. ✅ `ByopSection.vue`: shown only when `use_user_palette` toggle is on; hex color swatch adder — native `<input type="color">` + hex text input; swatches rendered as round glossy sticker dots with `var(--shadow-sticker-sm)`; remove button per swatch; `allow_color_reuse` toggle; builds `user_palette_hex[]`

### ✅ Phase 6 — Processing Screen (COMPLETED)

26. ✅ `ProcessingScreen.vue`: centered card — spinning indigo ring animation (CSS `@keyframes spin`, border-top lime), status text ("Generating your paint-by-numbers..." / "Processing...") in `var(--font-display)` 700; job id shown small in `var(--font-body)`
27. ✅ `useJobPoller.js` clears on `done` or `failed`, then jobStore updates trigger conditional re-render in `StudioView`

### ✅ Phase 7 — Results Screen (COMPLETED)

28. ✅ `ResultsScreen.vue`: three image preview cards (outline / color / palette) as sticker-style cards, slightly rotated; "Download ZIP" button: prominent lime sticker button; individual download link per file as smaller indigo/lavender buttons; 1-hour expiry notice in small `var(--color-lavender)` text
29. ✅ All download URLs taken directly from `jobStore.downloadUrls` — never constructed manually

### ✅ Phase 7.5 — Job ID in URL (COMPLETED)

**Goal:** Make the active job's ID part of the URL so processing and results screens are bookmarkable/shareable within the same browser session.

**Route change:**
- `/studio` — upload form (no job ID)
- `/studio/:jobId` — processing or results; screen toggled by `jobStore.status` as before

**Files to update:**

30. ✅ `src/main.js` router: route changed from `/studio` to `/studio/:jobId?` with `name: 'studio'`
31. ✅ `StudioView.vue`: `onMounted` re-hydrates from `route.params.jobId` via `getJob()`; `watch(jobStore.id)` mirrors ID to URL via `router.replace()`; `startOver()` calls `router.push({ name: 'studio' })` + `jobStore.reset()`; brief spinner shown while re-hydrating
32. ✅ `useJobPoller.js`: no change needed — it reads `jobStore.id` which is set by re-hydration
33. ✅ `AppHeader.vue`: "Start Creating →" link target stays `/studio` (no ID)

**Constraints / known limits:**
- Anonymous jobs are scoped to the Django session cookie — a URL opened in a different browser or incognito tab will receive a 404. Organizer jobs are scoped to the organizer's JWT identity; attendee jobs are scoped to the attendee context in the Django session.
- No server-side rendering; re-hydration is client-only

### ✅ Phase 8 — History Panel (COMPLETED)

34. ✅ `HistoryPanel.vue`: slide-in panel from right (`translateX` transition, 0.25s); semi-transparent backdrop with `fade` transition; fetches `historyStore.fetchHistory()` on open via `watch(props.open)`; loading spinner + error + empty states; job list as sticker cards
35. ✅ Status badges: lime=done, lavender=processing/pending, pink=failed
36. ✅ Clicking a `done` row: `emit('close')` + `router.push({ name: 'studio', params: { jobId: job.id } })` — `StudioView.onMounted` handles the re-hydration (Phase 7.5 integration)
37. ✅ Non-done rows are display-only (no cursor/click)

### ✅ Phase 9 — Error Handling (COMPLETED)

38. ✅ `src/api/jobs.js`: `apiFetch` now attaches `error.retryAfter` from the `Retry-After` response header on 429 responses
39. ✅ `src/utils/parseApiError.js`: normalises any thrown API error into a human-readable string — network failure, 400 field errors (flattened), 402 daily limit, 404 not found, 429 rate limit with countdown, all others via `detail`/`error` fallback
40. ✅ `ErrorBanner.vue`: dismissible banner — `--color-pink` left border, `--color-snow` background, sticker shadow; accepts `message` prop; emits `dismiss`; `role="alert"` + `aria-live="assertive"` for screen readers
41. ✅ `UploadPanel.vue`: replaced plain `<p>` error with `<ErrorBanner>`; `catch` now calls `parseApiError(err)` instead of manually inspecting `err.data`

---

## Decisions

| # | Decision | Rationale |
|---|---|---|
| 1 | Use `/studio/:jobId?` optional param (single route) instead of two separate routes | Keeps `StudioView` as one component; upload screen is just the `jobId === undefined` state |
| 2 | Re-hydrate from URL on mount via `getJob()`, not from localStorage | Backend is the source of truth; avoids stale state; consistent with how the poller works |
| 3 | Show a minimal "Fetching job…" loading state during re-hydration | Without it, the screen flashes the upload form before redirecting — jarring UX |
| 4 | Do not persist session cookie cross-device; show a clear 404 message if job not found | Jobs are anonymous-session-scoped; cross-device sharing isn't supported and shouldn't silently fail |
| 5 | `startOver()` navigates to `/studio` (no param) | Cleanly resets URL and store in one action; back button still works |

---

## Key Architecture Rules
- **theme.css is the only place** colors, shadows, fonts, and spacing are defined — all components consume via CSS custom properties
- Vite proxy handles `/api` → no CORS, no backend change
- `HeroBackground.vue`: only decorative shapes/animations, no text or layout whatsoever
- `HeroContent.vue`: no `position: absolute`, no `background`, no decorative styles — only layout, text, and CTA
- `useJobPoller` always clears its interval in `onUnmounted`
- CSRF token read from `document.cookie` at request time (not stored in state); organizer authentication uses bearer JWTs, while anonymous and attendee flows remain session-backed

---

## Verification
1. `npm run dev` → app loads at `localhost:5173`, dark `#1B1C1E` background visible immediately
2. Sticker aesthetic check: all cards/buttons have hard zero-blur shadows and thick borders
3. Upload a test image in Studio → job appears in Django SQLite `jobs_job` table
4. Polling reaches `done` → ResultsScreen shows image previews and ZIP button
5. ZIP download works; all three individual images downloadable
6. BYOP: add 3 hex swatches → submit → confirm `user_palette_hex` in Django job record
7. Submit 4 jobs same day → 4th returns 402 → "daily limit" banner appears
8. `HeroBackground.vue` contains zero text nodes; `HeroContent.vue` contains zero `position: absolute` elements — verify via code review
9. Delete all `var(--color-*)` from theme.css → every color in app breaks uniformly (confirms no hard-coded colors anywhere)
