# Plan: Standard Colour Paint Sets — Backend

## TL;DR
Add a new `palettes` Django app with `PaintSet` + `PaintColor` models, seed them via fixtures, and expose a single read-only list endpoint at `GET /api/palettes/`. No changes to the `jobs` app or pipeline needed.

## Steps

### Phase 1 — App & Models
1. Create new app `palettes/` inside `paintober_backend/` (`python manage.py startapp palettes`)
2. Add `PaintSet` model (SlugField PK, name, description, paint_type, tube_count)
3. Add `PaintColor` model (auto BigAutoField PK, FK to PaintSet, name CharField, hex CharField max_length=7)
4. Register `palettes` in `INSTALLED_APPS` (settings.py)
5. Register models in `palettes/admin.py` with inline for colors

### Phase 2 — Migration & Fixtures
6. Generate migration: `makemigrations palettes`
7. Create `palettes/fixtures/paint_sets.json` — 7 PaintSet records (corrected: drop the placeholder `colored_pencils_12` / `colored_pencils_24` PKs that had no color data; use the 7 real sets: beginner_acrylic_12, studio_acrylic_24, pastel_picnic, vibrant_party, earthy_neutrals, staedtler_noris_12, staedtler_noris_24)
8. Create `palettes/fixtures/paint_colors.json` — all color rows for all 7 sets (full data from spec)

### Phase 3 — API
9. Create `palettes/serializers.py` — `PaintColorSerializer` (name, hex), `PaintSetSerializer` (id, name, description, paint_type, tube_count, colors nested read-only)
10. Create `palettes/views.py` — `PaletteListView(ListAPIView)`, permission AllowAny, no throttle needed (read-only public data)
11. Create `palettes/urls.py` — `path("", PaletteListView.as_view(), name="palette-list")`
12. Register in `paintober_backend/urls.py` — `path("api/palettes/", include("palettes.urls"))`

### Phase 4 — Verification
13. `python manage.py migrate`
14. `python manage.py loaddata paint_sets paint_colors`
15. `GET /api/palettes/` returns 7 sets with nested colors
16. Check `/api/schema/swagger-ui/` shows the new endpoint

## Relevant files
- `paintober_backend/paintober_backend/settings.py` — add `palettes` to INSTALLED_APPS
- `paintober_backend/paintober_backend/urls.py` — add route
- `paintober_backend/jobs/models.py` — no changes
- `paintober_backend/jobs/serializers.py` — no changes
- New: `paintober_backend/palettes/models.py`
- New: `paintober_backend/palettes/serializers.py`
- New: `paintober_backend/palettes/views.py`
- New: `paintober_backend/palettes/urls.py`
- New: `paintober_backend/palettes/admin.py`
- New: `paintober_backend/palettes/fixtures/paint_sets.json`
- New: `paintober_backend/palettes/fixtures/paint_colors.json`
- New: `paintober_backend/palettes/migrations/0001_initial.py` (generated)

## Decisions
- New standalone `palettes` app, not merged into `jobs`, keeps concerns separate
- Drop `colored_pencils_12` / `colored_pencils_24` from fixture — no color data, replaced by the Noris-style sets which cover the same intent
- `paint_type` stored as a free CharField (not choices enum) to stay flexible
- Endpoint is read-only, public, unauthenticated — palettes are static reference data
- No pagination needed (7 sets, small payload)
