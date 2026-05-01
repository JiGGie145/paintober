## Plan: Standard Colour Paint Sets — UI

### TL;DR
Redesign the palette area in `UploadPanel` into a **3-tile radio card section** ("Choose your paint colors"). The three modes are Auto / Preset / BYOP. Selecting Preset lazily fetches `GET /api/palettes/` and expands a card grid. Selecting BYOP shows the existing hex-picker builder. `paletteMode` lives in `UploadPanel` and drives what gets sent to the API.

### Phase 0 — Backend: Add tag field to PaintSet
1. Add `tag = models.CharField(max_length=80, blank=True, default="")` to `PaintSet` model in `palettes/models.py`
2. `makemigrations palettes` → generates `0002_paintset_tag.py`
3. Update `palettes/fixtures/paint_sets.json` — add tag values: pastel_picnic → "Popular for dates", vibrant_party → "Great for events", earthy_neutrals → "", staedtler_noris_12 → "School favourite", staedtler_noris_24 → "School favourite", beginner_acrylic_12 → "", studio_acrylic_24 → "Great for events"
4. `loaddata paint_sets` (colors unchanged; use `--app palettes` to scope)
5. `PaintSetSerializer` in `palettes/serializers.py` — add `"tag"` to `fields` list

### Phase 1 — Frontend: API + data layer
6. Create `src/api/palettes.js` — export `getPalettes()` calling `GET /api/palettes/`
7. Create `src/composables/usePalettes.js` — lazy fetch pattern: `palettes` ref (null until fetched), `loading`, `error`, `fetchPalettes()` (no-op if already loaded). Called on first click of preset tile.

### Phase 2 — Frontend: New components
8. `PresetCard.vue` — props: `paintSet` object, `selected` bool. Shows: name, color swatch row (tiny circles), description, tag badge if `paintSet.tag`. Emits `select`. Highlighted ring + checkmark when selected. *(parallel with 9, 10)*
9. `PresetGrid.vue` — props: `palettes`, `loading`, `selectedId`. Renders grid of `PresetCard`s; skeleton loading state; horizontal scroll on mobile. Emits `select`. *(parallel with 8, 10)*
10. `PaletteSelector.vue` — the 3-tile container. Props: `params`, `paletteMode`, `palettes`, `palettesLoading`. Emits `update:paletteMode`, `update:params`. Contains the three radio cards and conditionally shows `PresetGrid` or `ByopSection` below. On preset tile click → calls `fetchPalettes()` from injected composable. *(parallel with 8, 9)*

### Phase 3 — Frontend: Wiring into UploadPanel
11. `UploadPanel.vue` — add `paletteMode` ref (`'auto'`|`'preset'`|`'byop'`) and `selectedPresetId` ref. Instantiate `usePalettes()`. Add watcher: when `paletteMode` changes to `'auto'`, reset `use_user_palette = false`, `user_palette_hex = []`. When a preset is selected, set `use_user_palette = true`, `user_palette_hex = [all hex values from that preset]`. Reorder template: dropzone → `PaletteSelector` → `ParametersPanel` → submit button.
12. `ParametersPanel.vue` — accept new `paletteMode` prop. Pass `paletteMode` down to `BasicParams`. Remove BYOP toggle row and `ByopSection` entirely (now owned by `PaletteSelector`).
13. `BasicParams.vue` — accept `paletteMode` prop. Hide `k_colors` row with `v-if="paletteMode !== 'preset'"`.

### Verification
1. Auto mode (default): submit sends no `use_user_palette`, k_colors slider visible
2. Select a preset: `user_palette_hex` array is populated with correct hex values, k_colors slider disappears in Advanced Settings
3. Switch to BYOP: grid collapses, hex-picker appears, previously selected preset is cleared from `user_palette_hex`
4. Switch back to Auto from any mode: `use_user_palette = false`, palette hex cleared
5. Mobile: preset cards scroll horizontally, swatches visible
6. `GET /api/palettes/` only called once per session (lazy + cached)

### Key files
- `paintober_backend/palettes/models.py` — add tag field
- `paintober_backend/palettes/serializers.py` — add tag to fields
- `paintober_backend/palettes/fixtures/paint_sets.json` — add tag values
- New: `paintober_frontend/src/api/palettes.js`
- New: `paintober_frontend/src/composables/usePalettes.js`
- New: `paintober_frontend/src/components/studio/PaletteSelector.vue`
- New: `paintober_frontend/src/components/studio/PresetGrid.vue`
- New: `paintober_frontend/src/components/studio/PresetCard.vue`
- `paintober_frontend/src/components/studio/UploadPanel.vue` — paletteMode state + layout reorder
- `paintober_frontend/src/components/studio/ParametersPanel.vue` — remove BYOP, pass paletteMode
- `paintober_frontend/src/components/studio/BasicParams.vue` — conditional k_colors hide

### Decisions
- `paletteMode` is frontend-only state; API contract unchanged (`use_user_palette` + `user_palette_hex`)
- BYOP section removed from ParametersPanel, lives only inside PaletteSelector tile 3
- k_colors slider hidden (not disabled) when preset active
- Featured tags added to backend (not hardcoded) per user decision
- Palettes fetched lazily, cached for the session in `usePalettes` composable
