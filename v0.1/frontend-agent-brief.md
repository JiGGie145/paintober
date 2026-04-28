# Paintober — Frontend Agent Brief

Use this document to build a frontend for the Paintober paint-by-numbers web app.
The backend is a Django REST API already running locally. Do not modify the backend.

---

## What the app does

Paintober converts a user-uploaded photo into a **paint-by-numbers kit**:

1. User uploads a photo (JPG, JPEG, PNG, or WEBP, ≤50 MB).
2. User optionally configures pipeline parameters.
3. The backend processes the image asynchronously (job queue).
4. When done, the user downloads up to 4 output files:
   - **Outline image** — black-line numbered regions (PNG)
   - **Color image** — simplified quantized version (PNG)
   - **Palette sheet** — color swatches with region numbers (PNG)
   - **ZIP** — all three in a single archive

---

## Base URL

```
http://localhost:8000
```

CSRF is required for unsafe methods (POST). Read the CSRF token from the cookie `csrftoken` and send it as the `X-CSRFToken` request header.

Sessions are used to scope jobs for anonymous users — the browser must send cookies with every request (`credentials: 'include'` / `withCredentials: true`).

---

## API Endpoints

### Live interactive docs
- Swagger UI: `GET /api/schema/swagger-ui/`
- ReDoc: `GET /api/schema/redoc/`
- OpenAPI JSON/YAML: `GET /api/schema/`

---

### 1. Submit a job

```
POST /api/jobs/create/
Content-Type: multipart/form-data
```

**Required field:**

| Field | Type | Notes |
|---|---|---|
| `image` | file | JPG / JPEG / PNG / WEBP, max 50 MB |

**Optional pipeline parameters:**

| Field | Type | Default | Range / Notes |
|---|---|---|---|
| `k_colors` | integer | 12 | 2–32. Number of colors in the palette. |
| `min_region_area` | integer | 200 | ≥1. Ignore regions smaller than this (px²). |
| `contour_epsilon` | float | 0.002 | 0.0001–0.05. Shape simplification factor. |
| `line_thickness` | integer | 1 | 1–10. Outline stroke width (px). |
| `apply_gaussian` | boolean | true | Pre-blur to reduce noise. |
| `min_label_spacing` | integer | 12 | 1–100. Minimum px between number labels. |
| `use_user_palette` | boolean | false | Enable Bring-Your-Own-Palette mode. |
| `user_palette_mode` | string | `"hex"` | `"rgb"` or `"hex"`. Which format the palette is in. |
| `user_palette_hex` | array of strings | — | e.g. `["#FF0000","#00FF00"]`. Required when `use_user_palette=true` and `user_palette_mode="hex"`. |
| `user_palette_rgb` | array of [R,G,B] arrays | — | e.g. `[[255,0,0],[0,255,0]]`. Required when `use_user_palette=true` and `user_palette_mode="rgb"`. |
| `allow_color_reuse` | boolean | true | Allow multiple regions to share a mapped palette color. |

**Successful response — HTTP 201:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending"
}
```

**Error responses:**

| Status | Meaning |
|---|---|
| 400 | Validation error, unsupported format, or file too large. Body: `{"detail": "..."}` or field-level errors. |
| 402 | Free daily limit reached (3 jobs/day for anonymous/unpaid users). Body: `{"detail": "..."}` |
| 429 | Rate limit exceeded (20 submissions/hour per user/session). |

---

### 2. Poll job status

```
GET /api/jobs/{job_id}/
```

`job_id` is a UUID.

**Response — HTTP 200:**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending" | "processing" | "done" | "failed",
  "retry_count": 0,
  "error_message": null,
  "parameters": {
    "k_colors": 12,
    "apply_gaussian": true
  },
  "created_at": "2026-04-27T10:00:00Z",
  "updated_at": "2026-04-27T10:00:05Z",
  "download_urls": null
}
```

When `status` is `"done"`, `download_urls` is populated:
```json
{
  "download_urls": {
    "outline": "http://localhost:8000/api/jobs/{id}/download/outline/?token=...",
    "color":   "http://localhost:8000/api/jobs/{id}/download/color/?token=...",
    "palette": "http://localhost:8000/api/jobs/{id}/download/palette/?token=...",
    "zip":     "http://localhost:8000/api/jobs/{id}/download/zip/?token=..."
  }
}
```

Download URLs include a **signed token** that expires after **1 hour**. Fetch them immediately on completion rather than storing for later.

**Returns 404** if the job does not belong to the current user/session.

---

### 3. List all jobs (current session/user)

```
GET /api/jobs/
```

**Response — HTTP 200:**
```json
[
  {
    "id": "...",
    "status": "done",
    "retry_count": 0,
    "created_at": "2026-04-27T10:00:00Z",
    "updated_at": "2026-04-27T10:00:10Z"
  }
]
```

Ordered by most recent first.

---

### 4. Download an output file

```
GET /api/jobs/{job_id}/download/{file_key}/?token={signed_token}
```

`file_key` is one of: `outline`, `color`, `palette`, `zip`.

Returns the raw file (`Content-Type: image/png` or `application/zip`).

Returns 403 if the token is expired or invalid, 404 if the job is not done or the file is missing.

**Always use the full URL from `download_urls`** — do not construct these URLs yourself.

---

## Job lifecycle

```
[user submits] → pending → processing → done
                                      ↘ failed (up to 2 retries)
```

Poll `GET /api/jobs/{job_id}/` every **5 seconds** until `status` is `"done"` or `"failed"`.

---

## Limits (free tier / anonymous)

| Limit | Value |
|---|---|
| Free jobs per calendar day | 3 |
| Max submissions per hour | 20 |
| Max upload size | 50 MB |
| Max image width (server-side resize) | 1500 px |
| Supported formats | JPG, JPEG, PNG, WEBP |
| Download link TTL | 1 hour |

---

## Suggested UI flow

1. **Upload screen** — drag-and-drop or file picker. Show format/size constraints.
2. **Parameters panel** — collapsible/optional. Sliders/inputs for `k_colors`, `line_thickness`, etc. BYOP section that appears when `use_user_palette` is toggled.
3. **Processing screen** — show spinner / progress indicator while polling. Display `status` text (`pending`, `processing`).
4. **Results screen** — show previews of the three images and a prominent "Download ZIP" button. Individual download links for each file. Show expiry notice for the 1-hour token window.
5. **History panel** — list from `GET /api/jobs/` showing past jobs with their status. Clicking a `done` job re-opens the results screen (re-fetches detail to get fresh download URLs).
6. **Error states** — handle 400 (show field errors), 402 (show upgrade prompt), 429 (show retry-after), 404, and network failures gracefully.

---

## BYOP (Bring Your Own Palette) feature

When `use_user_palette` is `true`, the pipeline maps the generated k-means colors to the nearest colors in the user-supplied palette. Useful for users who own a fixed set of physical paints.

UI suggestion: a color swatch picker where users add colors manually (hex input or color picker). Send as `user_palette_hex` array. The `allow_color_reuse` toggle controls whether multiple regions can share the same paint.

---

## Notes for the agent

- Authentication is **not implemented** in v0.1. All endpoints are open (`AllowAny`). Session cookies are the only ownership mechanism.
- There is no WebSocket/SSE — use plain HTTP polling.
- The backend runs with `DEBUG=True` and SQLite. CORS is not yet configured — run the frontend on the same origin or add `django-cors-headers` to the backend if using a separate dev server.
- The OpenAPI schema is auto-generated by `drf-spectacular` and always reflects the current API. Consult `/api/schema/swagger-ui/` for the live spec.
