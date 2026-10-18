---
doc: roadmap
format: gam-engineering/2
title: Roadmap
audience: [product, developer, reviewer, agent]
---
# Roadmap

The ordered list of features this project plans to build, for everyone who wants to know what comes next and why (P-ROAD-1). The order follows dependencies, not dates. Only the lifecycle stage of each feature is tracked here; where work currently stands is in [ROADMAP-DETAILS.md](ROADMAP-DETAILS.md).

## Overview

| Version | Feature | Serves | Status | Depends on | Feasibility |
| --- | --- | --- | --- | --- | --- |
| 1.1.0 | HA version readiness | G-1 (runs on every current HA version, installable via HACS), G-1.S1, G-1.S2 | concept | — | high |
| 1.2.0 | Clean reload | G-1 (reliable monitoring), G-1.S3 | concept | HA version readiness | medium |

*Serves* names the part of the project goal in [GOAL.md](GOAL.md) this feature advances (P-GOAL-2).

*Status* is one of these stages (P-ROAD-1), updated at every phase boundary, merge, and release (P-ROAD-4). The branch model is `trunk` (P-GIT-9), so `merged` replaces `in dev`.

| Stage | Meaning |
| --- | --- |
| idea | Listed, no concept document yet |
| concept | Concept document in Phases 1–6 |
| ready | Concept approved, issues cut, nothing merged yet |
| in progress | At least one issue being implemented or merged, not all |
| merged | All stories merged into `main`, not yet released |
| released | Part of a release tag on `main` |

## Feature notes

### HA version readiness

- **What it gives users:** The integration loads without deprecation warnings on the current Home Assistant release, a weekly CI run warns the maintainer before a coming release breaks it, and it installs and updates through HACS.
- **Why this position:** Replacing deprecated APIs and adding CI make every later change safe to ship.
- **Feasibility:** High. All affected code places are known; open point A3 (whether the options flow already fails on 2026.10) is verified in HAR-US-1.
- **Concept document:** [concepts/ha-major-readiness.md](concepts/ha-major-readiness.md)

### Clean reload

- **What it gives users:** Reloading or removing the integration works without restarting Home Assistant and leaves no open connection to the heat pump.
- **Why this position:** It rebuilds the internal structure (`runtime_data`, coordinator) and is only safe once the tests and CI of the first feature exist (concept Q14).
- **Feasibility:** Medium. It touches every platform file; the tests from HAR-US-2 guard against regressions.
- **Concept document:** [concepts/ha-major-readiness.md](concepts/ha-major-readiness.md)
