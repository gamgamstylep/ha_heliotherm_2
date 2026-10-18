---
doc: roadmap-details
format: gam-engineering/2
title: Roadmap details
audience: [developer, reviewer, agent]
---
# Roadmap Details

Where the project stands right now, for anyone starting a work session — human or agent (P-ROAD-2). It is the single status entry point: a fresh session needs no chat history. Other documents link here and never copy this status.

## Current positions (solo mode)

| Feature | Concept document | Phase | Branch | MR | Next step |
| --- | --- | --- | --- | --- | --- |
| HA version readiness | [concepts/ha-major-readiness.md](concepts/ha-major-readiness.md) | 1 — concept written, merged into `main` | — | — | `/gam-engineering tickets ha-major-readiness` (cut E01 into GitHub issues) |
| Clean reload | [concepts/ha-major-readiness.md](concepts/ha-major-readiness.md) | 1 — concept written, merged into `main` | — | — | Starts after HA version readiness is released (v1.1.0) |

## Log

| Date | Handle | Task | Outcome | Done |
| --- | --- | --- | --- | --- |
| 2026-10-18 | — | Fix Modbus timeout crash, add reachability sensor, fix uint32 counters | Merged into `main` (`e06f2ec`), tested live in Home Assistant | ✔ |
| 2026-10-18 | — | Make the project ready for the next major Home Assistant versions | Slim setup (Q8–Q10), goal `G-1`, concept with epics E01 (v1.1.0) and E02 (v1.2.0), Q11–Q18; concept merged into `main` | ✔ |
