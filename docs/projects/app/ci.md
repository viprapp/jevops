# App CI (Stage 3)

This repo uses GitHub Actions to ensure every PR is validated and every merge to
`main` produces a deployable artifact.

## Goals (Stage 3)

- PRs: fail fast on docs + workflow mistakes, and prove the app still boots.
- main: publish a container image to GHCR.

## Workflows involved

- `.github/workflows/ci.yml`
  - Lints GitHub Actions workflows (actionlint)
  - Docs quality checks (markdownlint + lychee)
  - PR-only: build container + smoke test via Docker Compose

- `.github/workflows/publish-image.yml`
  - Builds the app image
  - Pushes to GHCR on `main`

## What runs on pull requests

### 1) Workflow lint: actionlint

Purpose: catch invalid inputs, typos, wrong action parameters, invalid contexts,
and similar mistakes before merge.

Where: `ci.yml` job `actionlint`

Expected outcome:

- Workflow YAML is valid
- Incorrect action inputs are rejected (for example, passing `context` to
  `docker/setup-buildx-action`, which does not support it)

### 2) Docs quality gates

Where: `ci.yml` job `docs-quality`

- Markdown lint (format consistency)
- Link check (keeps repo clean)

### 3) App container: build + smoke test

Where: `ci.yml` job `app-container-pr`

Steps:

1. Build the app image with Buildx (`docker/build-push-action`) and load it into
   the runner Docker daemon.
2. Start the Compose stack from `projects/app/`.
3. Validate the HTTP health endpoint.

Smoke test commands (conceptually):

- `docker compose up -d --wait`
- `docker compose ps`
- `curl http://localhost:8000/healthz`

Notes:

- The curl check can fail if the app container is still starting even though
  Compose has started the container. The job should rely on service health and
  /or retry the curl check briefly.

## What runs on push to main

### Publish container image to GHCR

Where: `publish-image.yml`

Image name:

- `ghcr.io/<owner>/<repo>/app`

Tags:

- `latest`
- `sha-<git-sha>` (or `sha` tag style produced by metadata-action)

Authentication:

- Uses `GITHUB_TOKEN` with `packages: write`

## Artifacts produced

- GHCR container image:
  - `ghcr.io/viprapp/jevops/app:latest`
  - `ghcr.io/viprapp/jevops/app:sha-...`

## How to verify quickly

### Check CI on a PR

- Open the PR
- Ensure these checks pass:
  - actionlint
  - docs-quality
  - app - build + smoke test (PR)

### Check publish on main

- Merge PR to `main`
- Confirm `publish-image` workflow run succeeded
- Confirm tags exist in GHCR for the repo

## Common issues and how we catch them

- Wrong paths (for example wrong Dockerfile path):
  - Caught by actionlint (workflow validation) and by the container build step
- Wrong action inputs:
  - Caught by actionlint (example: invalid inputs to setup-buildx-action)
- Compose starts but app not ready yet (curl reset/refused):
  - Fix by waiting for health or adding small curl retry loop
