# Cloud Run worker

`Dockerfile.cloudrun-worker` packages the one-shot
`run_poll_and_process` management command. Deploy it as a **Cloud Run Job**.
Cloud Run Services require an HTTP server listening on `$PORT`, so they are not
the right execution model for this command.

## Build and deploy

Run these commands from `paintober_backend/`:

The worker image builds the repository-local Rust extension from
`../rust/paintober_native` in a separate builder stage. The final image only
contains the compiled Python wheel; Rust and Cargo are not included at runtime.
The native merge backend is selected with
`PAINTOBER_MERGE_BACKEND=auto|native|python`. Use `auto` in deployment so the
worker uses Rust when installed and retains the Python fallback.

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/paintober-worker:latest \
  --file Dockerfile.cloudrun-worker

gcloud run jobs deploy paintober-worker \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/paintober-worker:latest \
  --region REGION \
  --set-env-vars GCS_ENABLED=True,GCS_PROJECT_ID=PROJECT_ID,GCS_UPLOAD_BUCKET_NAME=UPLOAD_BUCKET,GCS_RESULTS_BUCKET_NAME=RESULTS_BUCKET,GCS_OBJECT_PREFIX=jobs,GCS_SIGNED_URL_EXPIRY_SECONDS=3600,PAINTOBER_MERGE_BACKEND=auto,VERTEX_AI_ENABLED=False,VERTEX_AI_PROJECT_ID=PROJECT_ID,VERTEX_AI_LOCATION=us-east1,VERTEX_AI_MODEL=gemini-3.1-flash-lite-image \
  --set-secrets SECRET_KEY=paintober-secret:latest,DB_PASSWORD=paintober-db-password:latest
```

Use Secret Manager for `SECRET_KEY`, database credentials, and any other
secrets instead of putting their values in shell history or source control.
The Cloud Run Job service account needs access to both GCS buckets and the
database. Add `--set-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME` only
when the database is hosted in Cloud SQL; for a Linode-hosted database,
configure its network access and `DB_HOST`/`DB_PORT` values instead.

## Enable cartoonish outline jobs

Cartoonish jobs call Vertex AI before the local outline renderer and are
disabled by default. Enable the Vertex AI API for the project and grant the
worker service account the Vertex AI User role (`roles/aiplatform.user`) before
setting `VERTEX_AI_ENABLED=True`. Keep `VERTEX_AI_PROJECT_ID`, location, and
model aligned with the enabled project and region.

The worker uses Application Default Credentials. On Cloud Run, prefer the
service account attached to the Cloud Run Job; do not put a service-account key
in the image or in `Job.parameters`. A local key may be supplied through
`VERTEX_AI_CREDENTIALS_PATH` only for development. Vertex quotas, request
timeouts, and model usage can affect both job latency and project cost, so set
project budgets and quotas before enabling the frontend flag.

## Execute

```bash
gcloud run jobs execute paintober-worker --region REGION --wait
```

Each execution claims and processes at most one pending job. Schedule repeated
execution with Cloud Scheduler, or trigger executions from the API/queue layer.

## Local native development

From the repository root, configure the Python 3.13 environment and build the
macOS arm64 wheel:

```bash
python -m pip install 'maturin>=1.8,<2'
python -m maturin develop --release \
  --manifest-path rust/paintober_native/Cargo.toml
python -m unittest paintober_backend.pipeline.test_merge_small_regions \
  paintober_backend.pipeline.tests
```

To force the compatibility implementation during diagnosis or rollback:

```bash
PAINTOBER_MERGE_BACKEND=python python manage.py run_poll_and_process
```

For deployment, build from the repository root so Docker can access both
`paintober_backend/` and `rust/`:

```bash
docker build --platform linux/amd64 \
  -f paintober_backend/Dockerfile.cloudrun-worker \
  -t REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/paintober-worker:latest .
```

## Required environment variables

The container also needs the same Django database and deployment settings as
the Linode API, including `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, and `DB_PORT` when using PostgreSQL. Configure them with
`--set-env-vars` for non-sensitive values and `--set-secrets` for credentials.
For cartoonish processing, also configure `VERTEX_AI_ENABLED`,
`VERTEX_AI_PROJECT_ID`, `VERTEX_AI_LOCATION`, and `VERTEX_AI_MODEL`.