---
doc: story
format: gam-engineering/2
title: "HAR-US-2 Detect breaks early"
audience: [product, developer, reviewer, agent]
id-prefix: "HAR"
status: backlog
sprint: ""
---
# HAR-US-2 Detect breaks early

One user story of [HA version readiness](epic.md) and the acceptance criteria that decide when it is done. This file is the single source for both; the story issue copies them verbatim (P-DOC-6, P-TRK-2).

## User story

| ID | Title | As a | I want | so that | Priority |
| --- | --- | --- | --- | --- | --- |
| HAR-US-2 | Detect breaks early | maintainer of the integration (R-2) | a CI run that checks the integration against the newest HA release every week | I learn about a break before I update my own HA | Must |

## Acceptance criteria

| ID | Title | Given | When | Then |
| --- | --- | --- | --- | --- |
| HAR-AC-2.1 | Checks on push | a push to any branch | the workflow `validate.yml` runs | the jobs `hassfest`, `hacs`, and `tests` run, and all three are green on `main` |
| HAR-AC-2.2 | Weekly run | Monday 04:00 UTC | the scheduled run starts | it installs the newest `pytest-homeassistant-custom-component`; if any job fails, the run is red and GitHub e-mails the maintainer |
| HAR-AC-2.3 | Seams tested | the test suite | `pytest` runs | tests pass for: config flow creates an entry; options flow sets `display_language`; setup and unload with a fake Modbus client; registers 60 = 0 and 61 = 56215 decode to 56215; a Modbus timeout sets entities `unavailable` and the reachability sensor `off` |

## Slices

| Slice | Delivers | Blocked by | Issue |
| --- | --- | --- | --- |
| 1 — CI and tests | HAR-AC-2.1, HAR-AC-2.2, HAR-AC-2.3 | — | — |

- **Story issue:** — (filled in by `/gam-engineering tickets`)
- **Weight:** 5
- **Depends on:** —
