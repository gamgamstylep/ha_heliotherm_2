---
doc: concept
format: gam-engineering/2
title: HA version readiness and clean reload
audience: [product, developer, reviewer, agent]
id-prefix: "HAR"
---
# HA Version Readiness and Clean Reload — Concept

This concept says what makes `ha_heliotherm_2` keep working through coming Home Assistant (HA) releases, and how a break is detected before an update. It is read by the maintainer and by any agent implementing the epics E01 (v1.1.0) and E02 (v1.2.0). Part H summarizes it in plain words; Part S is normative.

# Part H — For Human Readers

## H1. In one sentence

The integration runs on every new HA version without failing or logging deprecation warnings, and a break caused by a coming version is detected before the update. This serves the part of `G-1` "lauffähig auf jeder aktuellen HA-Version, installierbar über HACS".

## H2. Who benefits and how

- **HA user with a Heliotherm heat pump (R-1):** HA updates no longer silently break the heat pump values; installing and updating works through HACS; from v1.2.0 on, changing settings reloads only this integration instead of needing an HA restart.
- **Maintainer (R-2):** a weekly CI run against the newest HA version turns red before a release breaks the integration, and GitHub sends an e-mail.

## H3. How it works, step by step

1. The code stops using HA functions that are deprecated or already removed ([HAR-US-1](../work-items/E01-ha-version-readiness/HAR-US-1-load-without-warnings.md) (load without warnings)).
2. A GitHub Actions workflow runs `hassfest`, the HACS check, and the tests on every push and every Monday ([HAR-US-2](../work-items/E01-ha-version-readiness/HAR-US-2-detect-breaks-early.md) (detect breaks early)).
3. The repository is cleaned up and released as v1.1.0, installable from HACS as a custom repository ([HAR-US-3](../work-items/E01-ha-version-readiness/HAR-US-3-install-via-hacs.md) (install via HACS)).
4. In v1.2.0 the internal structure moves to HA's current pattern, so the integration can be reloaded and removed cleanly ([HAR-US-4](../work-items/E02-clean-reload/HAR-US-4-clean-reload.md) (clean reload)).

## H4. What it deliberately does not do

No new sensors or functions, no change to entity names or IDs, no listing in the HACS default list (`G-1.N3`), no other protocols or brands (`G-1.N1`, `G-1.N2`).

## H5. How it is built, in plain words

v1.1.0 changes only the places listed in §4 and adds a CI workflow with tests that replace the real heat pump with a fake Modbus client. v1.2.0 keeps the data of each configured heat pump on its config entry instead of in a global dictionary, and lets HA's standard update coordinator do the polling (§16).

## H6. How we know it works

Each story has acceptance criteria with concrete values. The tests in §17 cover the configuration dialog, setup and unload, register decoding, and the "not reachable" path; the live check against the real HA instance (via the Home Assistant MCP server) confirms the log is free of warnings.

## H7. Key decisions

- Two releases instead of one, to keep each step small (Q14).
- Tests run against the newest HA test package, so the weekly run notices new HA versions by itself (Q13, F-8).
- HACS custom repository only (Q15).
- `runtime_data` and coordinator form one story with two slices (Q16).

# Part S — Specification (normative)

## 0. Synthesis Context

Written on 2026-10-18 against HA 2026.10.2 (Python 3.14) after the fixes merged in `e06f2ec`. Findings in the code at that time:

| ID | Finding | Place |
| --- | --- | --- |
| K-1 | `OptionsFlowHandler.__init__` assigns `self.config_entry`; HA deprecated this in 2024.11 and announced it stops working in 2025.12. The class body is defined twice. | `config_flow.py` |
| K-2 | `FlowResult` is used instead of `ConfigFlowResult`. | `config_flow.py` |
| K-3 | `hass.add_job(coroutine)` schedules the climate write. | `ha_heliotherm_modbus_climate.py` |
| K-4 | `from homeassistant.components.input_number import *` (wildcard import from an unrelated integration). | `binary_sensor.py`, `climate.py` |
| K-5 | `async_setup` exists without `CONFIG_SCHEMA`. | `__init__.py` |
| K-6 | Global state in `hass.data[DOMAIN]`, own timer instead of a coordinator. | `__init__.py`, platform files |
| K-7 | Stale files: root `manifest.json` (pins `pymodbus==3.8.6`), root `translations/`, `__init__ copy.py`, `manifest copy.json`, `heliotherm_config copy.json`, `.lnk` shortcuts inside the component. | repository |
| K-8 | `hacs.json` declares minimum HA `0.100.0` and `zip_release: true` without a release asset. | `hacs.json` |
| K-9 | No CI, no tests. | repository |

## 1. Purpose & Goal Trace

| ID | Feature goal | Serves |
| --- | --- | --- |
| HAR-FG | Die Integration läuft auf jeder neuen HA-Version ohne Abbruch oder Deprecation-Warnung; ein Bruch durch eine kommende Version wird vor dem Update erkannt. | `G-1` (lauffähig auf jeder aktuellen HA-Version, installierbar über HACS), `G-1.S1`, `G-1.S2`, `G-1.S3` |

## 2. Ubiquitous Language & Context

| Term | Meaning |
| --- | --- |
| Hub | `HaHeliothermModbusHub`: owns the Modbus TCP client and the polled register values of one heat pump. |
| Config entry | HA's stored configuration of one heat pump (host, port, name, access mode, display language). |
| Deprecation warning | A log line from HA about `ha_heliotherm_2` containing `deprecated`, `will stop working`, or `Detected that custom integration`. |
| uint32 counter | A 32-bit value whose high word is in register `n-1` and low word in register `n`. |
| Scheduled run | The weekly CI run on `main`, Monday 04:00 UTC. |

## 3. User Stories & Acceptance Criteria

The work items are the single source (P-DOC-6):

| Epic | Release | Stories |
| --- | --- | --- |
| [E01 HA version readiness](../work-items/E01-ha-version-readiness/epic.md) | 1.1.0 | HAR-US-1 (load without warnings), HAR-US-2 (detect breaks early), HAR-US-3 (install via HACS) |
| [E02 Clean reload](../work-items/E02-clean-reload/epic.md) | 1.2.0 | HAR-US-4 (clean reload) |

## 4. Functional Requirements

| ID | Title | Requirement | Derives from |
| --- | --- | --- | --- |
| HAR-F-1 | Options flow without own entry | `OptionsFlowHandler` MUST NOT assign `self.config_entry` and MUST NOT define `__init__` taking the entry; `async_get_options_flow` MUST return `OptionsFlowHandler()`. The class MUST be defined exactly once. | HAR-AC-1.2 |
| HAR-F-2 | Current flow result type | Config and options flow steps MUST be annotated with `ConfigFlowResult`; `FlowResult` MUST NOT be imported. | HAR-AC-1.1 |
| HAR-F-3 | Awaited climate write | `HaHeliothermModbusClimate` MUST implement `async_set_temperature` and await `hub.setter_function_callback`; `hass.add_job` MUST NOT be used anywhere in the component. | HAR-AC-1.3 |
| HAR-F-4 | No foreign wildcard imports | The component MUST NOT use `import *`, and MUST NOT import from `homeassistant.components.input_number`. | HAR-AC-1.1 |
| HAR-F-5 | Config-entry-only schema | `__init__.py` MUST define `CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)`. | HAR-AC-1.1 |
| HAR-F-6 | CI workflow triggers | `.github/workflows/validate.yml` MUST run on `push`, `pull_request`, `workflow_dispatch`, and `schedule` with cron `0 4 * * 1`. | HAR-AC-2.1, HAR-AC-2.2 |
| HAR-F-7 | CI jobs | The workflow MUST have three jobs: `hassfest` (`home-assistant/actions/hassfest`), `hacs` (`hacs/action`, category `integration`), and `tests` (pytest). | HAR-AC-2.1 |
| HAR-F-8 | Tests follow the newest HA | `requirements_test.txt` MUST list `pytest-homeassistant-custom-component` without an upper version bound, so every scheduled run tests against the newest HA release. | HAR-AC-2.2 |
| HAR-F-9 | Tested seams | Tests MUST cover: config flow creates an entry; options flow updates `display_language`; setup and unload with a fake Modbus client; uint32 decoding (§10); a Modbus timeout sets all entities `unavailable` and the reachability sensor `off`. | HAR-AC-2.3 |
| HAR-F-10 | No stale files | The files listed in K-7 MUST be removed from the repository. | HAR-AC-3.2 |
| HAR-F-11 | HACS metadata | `hacs.json` MUST set `zip_release` to `false` (or remove it) and `homeassistant` to the minimum HA version determined under A4. | HAR-AC-3.1 |
| HAR-F-12 | Release | The `version` in `custom_components/ha_heliotherm_2/manifest.json` MUST equal the release tag without `v` (`1.1.0` ↔ `v1.1.0`); every release MUST be a GitHub Release with release notes (P-VER-1). | HAR-AC-3.3 |
| HAR-F-13 | Runtime data on the entry | From v1.2.0, the hub MUST be stored in `entry.runtime_data`; per-entry data MUST NOT be stored in `hass.data[DOMAIN]`. | HAR-AC-4.1 |
| HAR-F-14 | Coordinator polling | From v1.2.0, polling MUST use a `DataUpdateCoordinator` with `update_interval` = `default_scan_interval` from `heliotherm_config.json`; a `ModbusException` MUST raise `UpdateFailed`. | HAR-AC-4.3 |
| HAR-F-15 | Clean unload | Unloading MUST unload all four platforms and close the Modbus connection before `async_unload_entry` returns `True`. | HAR-AC-4.2 |

## 5. User Interaction Requirements

| ID | Title | Requirement | Derives from |
| --- | --- | --- | --- |
| HAR-U-1 | Unchanged options dialog | The options dialog MUST keep its fields host, port, access mode, and display language with their current defaults. | HAR-AC-1.2 |

## 6. Non-Functional Requirements

| ID | Title | Requirement | Derives from |
| --- | --- | --- | --- |
| HAR-NF-1 | Stable entity IDs | `unique_id` and `entity_id` of every existing entity MUST stay unchanged (A1), so history, statistics, and automations keep working. | `G-1` |
| HAR-NF-2 | Same values | With the same `heliotherm_config.json`, every entity MUST show the same value as before the change for the same register contents. | `G-1` |
| HAR-NF-3 | CI duration | One CI run MUST finish in at most 10 minutes. | HAR-US-2 |
| HAR-NF-4 | No warnings | `ha_heliotherm_2` MUST log 0 deprecation warnings on the current stable HA release. | `G-1.S1` |

## 7. Capability Requirements

| ID | Title | Requirement |
| --- | --- | --- |
| HAR-C-1 | CI host | A CI service on the git host that runs on push, pull request, and a weekly schedule and e-mails the maintainer on failure (GitHub Actions). |

## 8. Data Model

No new persistent data. Config entry fields are unchanged.

## 9. Error Conditions

| ID | Title | Trigger | Required behavior | Fallback | Derives from |
| --- | --- | --- | --- | --- | --- |
| HAR-E-1 | Scheduled run fails | A new HA release breaks a test or `hassfest` | The run is red and GitHub e-mails the maintainer; the maintainer does not update the production HA before the run is green again. | Pin HA in production until fixed. | HAR-AC-2.2 |
| HAR-E-2 | Heat pump not reachable | No Modbus response | All entities `unavailable`, reachability sensor `off`, one warning in the log per outage. | — | HAR-AC-4.3 |

## 10. Worked Examples

| Rule | Input | Output |
| --- | --- | --- |
| uint32 counter | register 60 = 0, register 61 = 56215 | 56215 |
| uint32 counter | register 72 = 1, register 73 = 12 | 65548 |
| Release version | tag `v1.1.0` | `manifest.json` `"version": "1.1.0"` |

## 11. Integration Points

HA core (config entries, entity platforms, update coordinator), pymodbus as bundled by HA's `modbus` integration, HACS, GitHub Actions.

## 12. Out of Scope

New entities or functions, register map changes, YAML configuration, HACS default list (`G-1.N3`).

## 13. Resolved Questions & ADRs

| Q | Decision | Rationale |
| --- | --- | --- |
| Q11 | Scope: deprecated APIs, CI, modernization, release hygiene | All four together make the integration ready for coming releases. |
| Q12 | Feature goal as in §1 | Includes early detection, not only current compatibility. |
| Q13 | Tests at the seams in CI | Catches breaks that `hassfest` cannot see (flows, setup, decoding). |
| Q14 | Two releases: v1.1.0, then v1.2.0 | Smaller risk per step; the refactor lands with tests in place. |
| Q15 | HACS custom repository | No default-list requirements needed. |
| Q16 | `runtime_data` and coordinator as one story with two slices | Only together do they give users a visible benefit. |

Assumptions:

| ID | Assumption |
| --- | --- |
| A1 | Entity and unique IDs stay unchanged (HAR-NF-1). |
| A2 | The scheduled run is weekly, Monday 04:00 UTC. |
| A3 | Whether the options flow already fails on HA 2026.10 is verified at the start of HAR-US-1; HAR-F-1 applies either way. |
| A4 | The minimum HA version is the first release whose `modbus` integration requires pymodbus ≥ 3.10 (needed for the `device_id` argument); it is looked up in the HA core repository during HAR-US-3. |

No ADR is required: no goal change and no deviation from a `P-…` ID.

## 14. Artifact Interactions & Interferences

`heliotherm_config.json` is read unchanged. The reachability sensor added on 2026-10-18 moves to the coordinator's `last_update_success` in v1.2.0.

## 15. Schema Extensions

None.

## 16. Architecture & Vertical Slices

| Slice | Story | Delivers |
| --- | --- | --- |
| 1 — CI and tests | HAR-US-2 | HAR-F-6…9 |
| 2 — Deprecated APIs | HAR-US-1 | HAR-F-1…5 |
| 3 — Release hygiene and v1.1.0 | HAR-US-3 | HAR-F-10…12 |
| 4 — Runtime data | HAR-US-4 | HAR-F-13, HAR-F-15 |
| 5 — Coordinator | HAR-US-4 | HAR-F-14 |

Slice 1 comes first so slice 2 is already guarded by tests.

## 17. Test Concept & TDD Contract

Tests live in `tests/` and use `pytest-homeassistant-custom-component`. The Modbus client is replaced by a fake at the seam `HaHeliothermModbusHub._client` (P-DES-2). Each test names the AC it proves. After each slice, the live HA instance is checked through the Home Assistant MCP server: log free of deprecation warnings, entities with values.
