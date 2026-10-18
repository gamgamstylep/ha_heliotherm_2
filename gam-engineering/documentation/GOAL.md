---
doc: goal
format: gam-engineering/2
title: Project goal
audience: [product, developer, reviewer, agent]
---
# Project Goal

What this project is for, in one sentence, for everyone who decides what gets built. It is the root of every document in `gam-engineering/documentation/`: everything else is derived from this page and must not contradict it (P-GOAL-1…3). Changing anything here is a deliberate decision: record an ADR, then re-check every roadmap feature, feature goal, and user story that depends on the changed part.

## Source

Project application: none. `G-1` was approved in [qa-log.md](qa-log.md), Q8.

## G-1 — Goal

> Heliotherm-Wärmepumpen lokal per Modbus TCP in Home Assistant zuverlässig überwachen und steuern – lauffähig auf jeder aktuellen HA-Version, installierbar über HACS.

## Target users

| ID | User group (role) | What they need from the product |
| --- | --- | --- |
| R-1 | Home Assistant user with a Heliotherm heat pump | Current heat pump values and settings in Home Assistant that keep working across Home Assistant updates. |
| R-2 | Maintainer of the integration | Early notice when a coming Home Assistant version would break the integration, and a simple way to ship a fix. |

The role names in user stories (`As a …`) are taken from this table.

## Success signals

| ID | Signal | Target |
| --- | --- | --- |
| G-1.S1 | Deprecation warnings logged by `ha_heliotherm_2` on the current stable Home Assistant release | 0 lines |
| G-1.S2 | Scheduled CI run against the latest Home Assistant version on `main` | green every week; a red run is fixed before the maintainer updates Home Assistant |
| G-1.S3 | Entities available while the heat pump answers Modbus requests | ≥ 99 % of polls per month |

## Non-goals

| ID | Non-goal | Why |
| --- | --- | --- |
| G-1.N1 | Cloud access or protocols other than Modbus TCP | The integration is local by design (`iot_class: local_polling`). |
| G-1.N2 | Heat pumps of other manufacturers | The register map in `heliotherm_config.json` is Heliotherm-specific. |
| G-1.N3 | Listing in the HACS default repository list | Distribution as a HACS custom repository is enough (concept Q15). |
