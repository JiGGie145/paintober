# Prompt — Turn Notebook Into Async Backend Service (Discovery Mode)

You are helping design the architecture for turning an existing Jupyter-notebook image processing pipeline into a reusable backend service that will be used inside a Django web application.

**Important:**
Do NOT generate code yet.
Do NOT jump straight into architecture decisions.
Your primary task is to ask high-quality architecture and product questions so we can design the right system.

---

## Context

We have already built an image-to-paint-by-numbers pipeline that:

* Takes an uploaded photo
* Generates a paint-by-numbers outline
* Generates a simplified color version
* Generates a paint palette image
* Exports final assets (images + zip)

The algorithm works well and produces good results.

We now want to convert this into a production feature inside a Django SaaS app.

---

## Critical Requirement

The pipeline must run **asynchronously** after a user uploads an image.

The user flow will be:

1. User uploads photo + chooses settings
2. Server accepts request quickly
3. A background job processes the image
4. User can check job status
5. User downloads results when finished

This is a **job-based processing system**, not a synchronous API.

---

## What You Should Do First

Before proposing any architecture, you must ask clarifying questions about:

### Product requirements

### Performance expectations

### Scaling expectations

### Storage & file lifecycle

### Failure & retry behaviour

### Deployment constraints

### Observability / monitoring

### Cost sensitivity

### Security / multi-tenancy

### Future roadmap possibilities

Assume the current pipeline exists but you have not seen its internal code.

You must uncover unknowns before suggesting solutions.

---

## Examples of the Depth Expected

Avoid shallow questions like:

* “Should we use Celery?”

Instead ask deeper questions like:

* How long does a job currently take?
* How large are typical uploads?
* How many jobs per day are expected initially vs long-term?
* Do results need to be stored permanently or expire?
* Can users re-download old jobs?
* Should users be notified when jobs finish?
* What happens if processing fails midway?
* Are jobs idempotent?
* Do we need rate limiting?
* Do jobs need priority tiers?
* Are we deploying to a single VPS or cloud infrastructure?
* How important is horizontal scalability vs simplicity?

---

## Your Output Format

1. Ask a structured list of questions grouped by topic
2. Ask follow-up questions where uncertainty is high
3. Only after we answer, you will propose architecture later.

Do not propose solutions yet. Only ask questions.
