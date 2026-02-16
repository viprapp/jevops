# Roadmap - DevOps and DevSecOps learning journey

This repo documents my hands-on progress in DevOps and DevSecOps.
I focus on outcomes and evidence (working code, pipelines, deployments, and
docs) instead of course notes.

## Principles (how this roadmap stays relevant)

- **Evidence-first:** A stage is only "done" if there is clickable proof in
  this repo.
- **Stay current:** Version-sensitive guidance (CI flags, GitHub settings,
  security tooling) is verified against primary docs before adoption.
- **Security-by-default:** Least privilege, no long-lived credentials when
- avoidable, and early supply chain signals (SBOM, provenance).
- **Shift-left:** Security and quality checks run early and automatically.

---

## Current status

- **Current focus:** Adding foundations and optimizing the roadmap
- **Now working on:** **Stage 1** - Foundations
- **Last completed:** **Stage 0** - Portfolio setup
- **Next up:** **Stage 2** - Containers

---

## Progress overview

| Stage | Goal (Outcome)            | Status | Evidence                                |
| ----: | ------------------------- | :----: | --------------------------------------- |
|     0 | Portfolio setup           |   🟩   | README, CI badge                        |
|     1 | Foundations               |   🟨   | `docs/foundations/`                     |
|     2 | Containers                |   ⬜   | `projects/app/`                         |
|     3 | CI/CD                     |   ⬜   | `.github/workflows/`                    |
|     4 | Cloud + IaC               |   ⬜   | `projects/iac/`                         |
|     5 | Kubernetes                |   ⬜   | `projects/k8s/`                         |
|     6 | DevSecOps + Observability |   ⬜   | `docs/security/`, `docs/observability/` |

**Status legend:** ⬜ planned - 🟨 in progress - 🟩 done

---

## Stages

### Stage 0 - Portfolio setup

**Outcome:** The repo is easy to navigate and demonstrates professional hygiene
and secure defaults.
**Evidence:** `README.md`, this roadmap, initial CI, repo rules.

- [x] Repo structure: `docs/`, `projects/`, `.github/workflows/`
- [x] `README.md` with highlights + quickstart
- [x] Basic CI on PR (lint/test)
- [x] Protect `main` using **rulesets** or branch protection (PR required,
      required checks).
- [ ] Set GitHub Actions token permissions to **least privilege** (read by
      default, elevate per job).

---

### Stage 1 - Foundations

**Outcome:** I can troubleshoot Linux/network issues and collaborate with Git
confidently.
**Evidence:** `docs/foundations/` (short notes + practical examples).

- [x] Linux basics (processes/services, permissions, logs)
- [x] Networking basics (DNS, HTTP/HTTPS, ports, debugging tools)
- [ ] Git workflow (branches, PRs, resolving conflicts)

---

### Stage 2 - Containers

**Outcome:** I can ship a small app as a container and run it locally with Compose.
**Evidence:** `projects/app/` (Dockerfile + Compose + run instructions).

- [ ] Docker fundamentals (images, layers, volumes, networking)
- [ ] Dockerfile best practices
- [ ] Docker Compose local environment

---

### Stage 3 - CI/CD

**Outcome:** Every change is tested, built, and deployed automatically with modern
security hygiene.
**Evidence:** `.github/workflows/` + workflow run history.

- [ ] PR checks (lint/test)
- [ ] Build and publish artifact (for example container image)
- [ ] Deploy on merge to `main`
- [ ] Use least-privilege `GITHUB_TOKEN` permissions in workflows.
- [ ] Prepare for secure deployments with **OIDC** (avoid long-lived cloud
      credentials where possible).

---

### Stage 4 - Cloud + IaC

**Outcome:** I can provision and deploy on a real cloud using Infrastructure as
Code.
**Evidence:** `projects/iac/` + docs showing reproducible setup.

- [ ] Pick one cloud platform (AWS or Azure or GCP)
- [ ] Terraform basics + remote state
- [ ] Public endpoint with HTTPS + DNS
- [ ] Prefer CI auth via OIDC over stored long-lived secrets when feasible.

---

### Stage 5 - Kubernetes

**Outcome:** I can run the same app on Kubernetes and update it safely.
**Evidence:** `projects/k8s/` + deployment notes.

- [ ] Deploy app to Kubernetes
- [ ] Ingress + configuration management
- [ ] Basic safe update strategy (documented)

---

### Stage 6 - DevSecOps + Observability (ongoing)

**Outcome:** Security and visibility are default - not an afterthought.
**Evidence:** `docs/security/`, `docs/observability/` + pipeline checks.

- [ ] CI security checks (secrets, dependencies, image scanning)
- [ ] Generate an **SBOM** (CycloneDX or SPDX) and publish as an artifact.
- [ ] Add build **provenance/attestations** for key artifacts when the pipeline
      stabilizes.
- [ ] Track repo security posture with OpenSSF **Scorecard** (periodic check,
      badge optional).
- [ ] Monitoring/logging basics + one alert
- [ ] One failure drill + short postmortem in `docs/postmortems/`
- [ ] (Optional) Map improvements to a recognized framework for credibility
      (NIST SSDF).

---

## Notes

- I keep stages intentionally high-level to avoid tool overload.
- Each stage is considered "done" only when there is clickable evidence in this
  repo.
- Repo and pipeline security practices follow modern guidance (shift-left, least
  privilege, OIDC, provenance, SBOM).
