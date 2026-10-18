---
doc: story
format: gam-engineering/2
title: "HAR-US-1 Load without warnings"
audience: [product, developer, reviewer, agent]
id-prefix: "HAR"
status: backlog
sprint: ""
---
# HAR-US-1 Load without warnings

One user story of [HA version readiness](epic.md) and the acceptance criteria that decide when it is done. This file is the single source for both; the story issue copies them verbatim (P-DOC-6, P-TRK-2).

## User story

| ID | Title | As a | I want | so that | Priority |
| --- | --- | --- | --- | --- | --- |
| HAR-US-1 | Load without warnings | Home Assistant user with a Heliotherm heat pump (R-1) | the integration and its options dialog to work on the current HA release without deprecation warnings | an HA update does not silently break my heat pump values | Must |

## Acceptance criteria

| ID | Title | Given | When | Then |
| --- | --- | --- | --- | --- |
| HAR-AC-1.1 | Clean start | HA 2026.10.2 with the integration configured for host 10.19.0.70 | HA starts | the log contains 0 deprecation warnings (concept §2) from `ha_heliotherm_2`, and all entities have values within 30 s |
| HAR-AC-1.2 | Options dialog works | the configured entry with display language `en` | the user opens *Configure*, selects `de`, and submits | the entry's `display_language` is `de`, the integration reloads, and no error is logged |
| HAR-AC-1.3 | Climate write awaited | access mode `read_write` and the climate entity for the normal hot-water temperature | the user sets 45 °C | the hub writes the register within the same service call (awaited), and `hass.add_job` is not used |

## Slices

| Slice | Delivers | Blocked by | Issue |
| --- | --- | --- | --- |
| 2 — Deprecated APIs | HAR-AC-1.1, HAR-AC-1.2, HAR-AC-1.3 | Slice 1 (HAR-US-2) | — |

- **Story issue:** — (filled in by `/gam-engineering tickets`)
- **Weight:** 3
- **Depends on:** HAR-US-2 — the tests of slice 1 guard this change (concept §16)
