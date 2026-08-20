

#### Build container: 

```sh
BUILDX_NO_DEFAULT_ATTESTATIONS=1 docker build --platform linux/amd64 --provenance=false -f Dockerfile.cloudrun-worker --tag us-east1-docker.pkg.dev/paintober/paintober-docker/paintober-backend:v0.1.x .
```
---
#### Push image to google artifact storage

```sh
docker push us-east1-docker.pkg.dev/paintober/paintober-docker/paintober-backend:v0.1.x
```
---
### Update image for `cloud run job`

```sh
gcloud run jobs update paintober-worker \
  --region=us-east1 \
  --image=us-east1-docker.pkg.dev/paintober/paintober-docker/paintober-backend:v0.1.x
```
---
#### trigger job

```sh
gcloud run jobs execute paintober-worker \
  --region=us-east1
```