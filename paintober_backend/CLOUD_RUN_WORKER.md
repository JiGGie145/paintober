# Cloud Run worker

`Dockerfile.cloudrun-worker` packages the one-shot
`run_poll_and_process` management command. Deploy it as a **Cloud Run Job**.
Cloud Run Services require an HTTP server listening on `$PORT`, so they are not
the right execution model for this command.

## Build and deploy

Run these commands from `paintober_backend/`:

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/paintober-worker:latest \
  --file Dockerfile.cloudrun-worker

gcloud run jobs deploy paintober-worker \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPOSITORY/paintober-worker:latest \
  --region REGION \
  --set-env-vars GCS_ENABLED=True,GCS_PROJECT_ID=PROJECT_ID,GCS_UPLOAD_BUCKET_NAME=UPLOAD_BUCKET,GCS_RESULTS_BUCKET_NAME=RESULTS_BUCKET,GCS_OBJECT_PREFIX=jobs,GCS_SIGNED_URL_EXPIRY_SECONDS=3600 \
  --set-secrets SECRET_KEY=paintober-secret:latest,DB_PASSWORD=paintober-db-password:latest
```

Use Secret Manager for `SECRET_KEY`, database credentials, and any other
secrets instead of putting their values in shell history or source control.
The Cloud Run Job service account needs access to both GCS buckets and the
database. Add `--set-cloudsql-instances PROJECT_ID:REGION:INSTANCE_NAME` only
when the database is hosted in Cloud SQL; for a Linode-hosted database,
configure its network access and `DB_HOST`/`DB_PORT` values instead.

## Execute

```bash
gcloud run jobs execute paintober-worker --region REGION --wait
```

Each execution claims and processes at most one pending job. Schedule repeated
execution with Cloud Scheduler, or trigger executions from the API/queue layer.

## Required environment variables

The container also needs the same Django database and deployment settings as
the Linode API, including `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`,
`DB_HOST`, and `DB_PORT` when using PostgreSQL. Configure them with
`--set-env-vars` for non-sensitive values and `--set-secrets` for credentials.