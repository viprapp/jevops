# Stage 1 - Foundations (evidence hub)

Goal: prove I can troubleshoot Linux and networking issues and collaborate with Git
using an evidence-first workflow (commands, logs, decision trail).

## What Stage 1 covers

- Linux fundamentals (services, logs, permissions, processes, troubleshooting)
- Networking fundamentals (DNS, HTTP/HTTPS, ports, TLS, isolating failures)
- Git fundamentals (GitHub Flow, PRs, merge conflicts)

## Evidence (labs)

### Linux

- Lab 1 - Service lifecycle + journald (sshd)
  `docs/foundations/labs/linux/lab-01-sshd.md`

- Lab 2 - DNS vs HTTP vs TLS: isolate the failure
  `docs/foundations/labs/linux/lab-02-dns-http-tls.md`

### Git

- Lab 3 - GitHub Flow + merge conflict
  `docs/foundations/labs/git/lab-03-github-flow.md`

## Quick reference notes

- Linux notes: `docs/foundations/linux.md`
- Networking notes: `docs/foundations/networking.md`
- Git notes: `docs/foundations/git.md`

## How to review Stage 1 (2-3 minutes)

1. Open Lab 2 first: it shows the clearest decision trail for diagnosing issues.
2. Check Lab 1: demonstrates service lifecycle + journald evidence.
3. Check Lab 3: shows PR workflow and a real merge conflict resolution trail.

## Definition of Done (Stage 1)

- [x] Linux lab includes: baseline -> controlled change -> logs -> recovery -> verification
- [x] Networking lab includes: DNS + HTTP + HTTPS + TLS inspection + conclusion
- [x] Git lab includes: PR flow + intentional conflict + resolution evidence
- [ ] Notes files (`linux.md`, `networking.md`, `git.md`) contain concise
      “what I can do” bullets
