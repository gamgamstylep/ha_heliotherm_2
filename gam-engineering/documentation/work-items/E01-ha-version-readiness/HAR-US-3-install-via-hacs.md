---
doc: story
format: gam-engineering/2
title: "HAR-US-3 Install via HACS"
audience: [product, developer, reviewer, agent]
id-prefix: "HAR"
status: backlog
sprint: ""
---
# HAR-US-3 Install via HACS

One user story of [HA version readiness](epic.md) and the acceptance criteria that decide when it is done. This file is the single source for both; the story issue copies them verbatim (P-DOC-6, P-TRK-2).

## User story

| ID | Title | As a | I want | so that | Priority |
| --- | --- | --- | --- | --- | --- |
| HAR-US-3 | Install via HACS | Home Assistant user with a Heliotherm heat pump (R-1) | to install and update the integration from HACS as a custom repository | I get fixes without copying files by hand | Must |

## Acceptance criteria

| ID | Title | Given | When | Then |
| --- | --- | --- | --- | --- |
| HAR-AC-3.1 | Install from HACS | HACS with the custom repository `https://github.com/gamgamstylep/ha_heliotherm_2` | the user installs the newest release | version 1.1.0 is installed in `custom_components/ha_heliotherm_2` and loads after an HA restart |
| HAR-AC-3.2 | Clean repository | the repository at tag `v1.1.0` | its files are listed | none of the stale files of concept K-7 exist |
| HAR-AC-3.3 | Matching release | the tag `v1.1.0` | the GitHub Releases page is opened | a release `v1.1.0` with release notes exists, and `manifest.json` contains `"version": "1.1.0"` |

## Slices

| Slice | Delivers | Blocked by | Issue |
| --- | --- | --- | --- |
| 3 — Release hygiene and v1.1.0 | HAR-AC-3.1, HAR-AC-3.2, HAR-AC-3.3 | Slices 1 and 2 | — |

- **Story issue:** — (filled in by `/gam-engineering tickets`)
- **Weight:** 3
- **Depends on:** HAR-US-1, HAR-US-2 — the release ships both
