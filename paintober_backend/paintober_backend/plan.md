## Plan: Paintober Async Backend Service (APScheduler edition)

**TL;DR** — Extract the notebook into a Django app. A `jobs` table acts as the queue. APScheduler runs a polling loop (as a management command supervised by systemd) that atomically claims pending jobs and processes them. No Redis, no Celery, no broker — just Django + SQLite + one background process.

---

### Phase 1 — Project Foundation
1. Install: `djangorestframework`, `django-apscheduler`, `Pillow`, `opencv-python`, `scikit-learn`, `numpy`, `matplotlib`
2. Update settings.py: add `MEDIA_ROOT`, `INSTALLED_APPS` additions (`rest_framework`, `django_apscheduler`, `jobs`, `pipeline`), file-based logging config, and `JOB_RATE_LIMIT_PER_HOUR = 20`, `FREE_JOBS_PER_DAY = 3` constants
3. Create two Django apps: `jobs` and `pipeline`

### Phase 2 — Pipeline Module *(no dependency on other phases)*
4. Extract all helper functions and 9 pipeline stages from the notebook into `pipeline/processor.py`
5. Single entry point: `run_pipeline(image_path: str, output_dir: Path, params: dict) -> dict` — returns dict of output file paths. All cell-3 and BYOP parameters accepted via `params` with notebook defaults as fallbacks
6. Strip all Jupyter/`plt.show()` calls; `create_palette_image()` uses `matplotlib.figure.Figure` + `savefig()` into a `BytesIO`, never displays
7. Input normalisation at upload time (before queuing): accept JPEG/PNG/WEBP, convert to PNG via Pillow

### Phase 3 — Job Model *(depends on Phase 1)*
8. `jobs/models.py` — `Job` model with: UUID PK, nullable `user` FK, `session_key` CharField (for anonymous), `status` choices (`pending`/`processing`/`done`/`failed`), `retry_count` IntegerField (default 0), `parameters` JSONField, `error_message` TextField (nullable), `input_file` CharField, four output path CharFields (`output_outline`, `output_color`, `output_palette`, `output_zip`), `created_at`/`updated_at`
9. File layout under `MEDIA_ROOT`: `uploads/{job_id}/original.png` and `outputs/{job_id}/{outline,quantized_color,palette,results.zip}`
10. Run and commit initial migration

### Phase 4 — Scheduler & Job Runner *(depends on Phases 2 & 3)*
11. Create `jobs/management/commands/run_scheduler.py` — a Django management command that starts APScheduler with an interval trigger (every 5 seconds)
12. The scheduled function `poll_and_process()`:
    - Inside a `transaction.atomic()` + `select_for_update(skip_locked=True)`, claim one `pending` job → set `status=processing`
    - Call `run_pipeline(...)` with the job's `params`
    - On success: save output paths, set `status=done`, create zip of the 3 PNGs, save `output_zip`
    - On exception: increment `retry_count`; if `retry_count < 2`, reset to `status=pending` for re-pick; if `retry_count >= 2`, set `status=failed`, save `error_message`, log to error log
13. Deployment: a systemd unit file `paintober-scheduler.service` running `python manage.py run_scheduler`, restarted on failure — *this is documented in the plan for the implementer, not generated as a file unless asked*

### Phase 5 — DRF API *(depends on Phases 3 & 4)*
14. `POST /api/jobs/` — validate file (reject >50 MB, non-image types); normalise format; enforce rate limit and free-tier check; save to `uploads/{job_id}/original.png`; create `Job` with `status=pending`; return `{job_id, status}`
15. `GET /api/jobs/{id}/` — return status; if `done`, include signed download URLs (1-hour expiry via `django.core.signing`) for each output file
16. `GET /api/jobs/` — list jobs scoped to authenticated user or session key
17. `GET /api/jobs/{id}/download/{file}/` — validate `django.core.signing` token; stream file from local disk using `FileResponse`
18. Wire into urls.py

### Phase 6 — Rate Limiting & Free Tier *(parallel with Phase 5)*
19. Custom DRF throttle `JobCreationThrottle` — scoped by user PK or session key, reads `settings.JOB_RATE_LIMIT_PER_HOUR`; returns 429 when exceeded
20. Free-tier guard in `POST /api/jobs/`: count jobs created today for the user/session; if ≥ `FREE_JOBS_PER_DAY` and user has no credits, return 402 with a clear message. `UserProfile.credits` field stubbed on the model for future billing integration

### Phase 7 — Admin & Logging *(parallel with Phase 5)*
21. `jobs/admin.py`: register `Job` with list display `[id, status, user, retry_count, created_at, error_message]`, filter by status, search by user/session
22. Settings logging config: `INFO+` → `logs/paintober.log`, `ERROR+` → `logs/errors.log`; log job claim, completion, failure, and retry events inside `poll_and_process()`

---

### Relevant Files
- settings.py — media, logging, constants, installed apps
- urls.py — include jobs API routes
- `paintober_backend/jobs/` — models, views, serializers, throttles, admin, management command
- `paintober_backend/pipeline/processor.py` — extracted from notebook

### Verification
1. `python manage.py run_scheduler` starts without error; APScheduler logs show interval job registered
2. `POST /api/jobs/` with a test PNG → job created with `status=pending`; scheduler picks it up within 5 seconds; `GET /api/jobs/{id}/` transitions to `done`
3. Signed download URL returns the correct file; a tampered/expired token returns 403
4. Force a `run_pipeline` exception → confirm `retry_count` increments; on 3rd failure `status=failed` and `error_message` populated
5. Submit 21 jobs in one hour → 21st returns 429
6. Submit 4 jobs in one day on free tier → 4th returns 402
7. `select_for_update(skip_locked=True)` confirmed by running two scheduler processes simultaneously and verifying no job is processed twice

---

### Decisions
- **APScheduler over Celery/Redis**: eliminates broker infrastructure; fits single-VPS, low-volume requirements perfectly
- **`skip_locked=True`**: safe for future horizontal scaling even on SQLite (though SQLite doesn't support `SKIP LOCKED` — if this becomes an issue, migrating to PostgreSQL unlocks it; for now, single scheduler process makes it moot)
- **5-second poll interval**: keeps latency low without hammering the DB; configurable via a settings constant
- **Zip generated post-processing** in the task, bundling all 3 PNGs
- **No BYOP image-mode in v1 API**: only `rgb` and `hex` palette modes exposed; image upload for palette adds multipart complexity for low gain

### Further Considerations
1. **SQLite + `select_for_update`**: SQLite does not support `SKIP LOCKED`. With a single scheduler process this is fine. If you ever run two scheduler processes, migrating to PostgreSQL is the clean fix. Worth noting now so it's not a surprise later.
2. **Scheduler process restart on deploy**: when deploying new code, the systemd unit needs a restart alongside gunicorn. Should the implementer add a `Makefile` or deploy script step for this?
3. **Credits model detail**: free/paid tier check stubs a `UserProfile.credits` field. Should the plan include the full `UserProfile` model + signal to create it on user registration, or leave that for a billing-focused plan?
