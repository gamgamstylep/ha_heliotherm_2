---
doc: story
format: gam-engineering/2
title: "HAR-US-4 Clean reload"
audience: [product, developer, reviewer, agent]
id-prefix: "HAR"
status: backlog
sprint: ""
---
# HAR-US-4 Clean reload

One user story of [Clean reload](epic.md) and the acceptance criteria that decide when it is done. This file is the single source for both; the story issue copies them verbatim (P-DOC-6, P-TRK-2).

## User story

| ID | Title | As a | I want | so that | Priority |
| --- | --- | --- | --- | --- | --- |
| HAR-US-4 | Clean reload | Home Assistant user with a Heliotherm heat pump (R-1) | to reload or remove the integration without restarting HA | changing a setting does not interrupt the rest of my home | Should |

## Acceptance criteria

| ID | Title | Given | When | Then |
| --- | --- | --- | --- | --- |
| HAR-AC-4.1 | Reload keeps working | the integration loaded with values | the user clicks *Reload* | all entities show values again within 30 s, no error is logged, and HA holds exactly 1 TCP connection to 10.19.0.70:502 |
| HAR-AC-4.2 | Remove closes the connection | the integration loaded | the user disables it | within 5 s HA holds 0 TCP connections to 10.19.0.70:502 |
| HAR-AC-4.3 | Outage and recovery | the heat pump stops answering Modbus | the next poll fails | all entities are `unavailable` and the reachability sensor is `off`; after the heat pump answers again, values return with the next poll |

## Slices

| Slice | Delivers | Blocked by | Issue |
| --- | --- | --- | --- |
| 4 — Runtime data | HAR-AC-4.1, HAR-AC-4.2 | E01 released | — |
| 5 — Coordinator | HAR-AC-4.3 | Slice 4 | — |

- **Story issue:** — (filled in by `/gam-engineering tickets`)
- **Weight:** 8
- **Depends on:** E01 — released as v1.1.0 first (concept Q14)
