# CLAUDE.md

Every grilling, planning, concept, or delivery session starts with /gam-engineering (P-GRILL-5, P-WS-6).

## Documentation

`gam-engineering/documentation/` is the source of truth: start with [GOAL.md](gam-engineering/documentation/GOAL.md), then [ROADMAP-DETAILS.md](gam-engineering/documentation/ROADMAP-DETAILS.md) for the current position. Branch model `trunk` and merge policy `ask` are set in `.claude/settings.json`. Plans go to `plans/`.

## Project overview

Home Assistant custom component `ha_heliotherm_2` for Heliotherm heat pumps via Modbus TCP (pymodbus async client). Register map and entity definitions live in `custom_components/ha_heliotherm_2/heliotherm_config.json`.

## Testing against the live Home Assistant

- The component is deployed by copying files to the Samba share `//10.19.0.34/config/custom_components/ha_heliotherm_2` (not via HACS). Python changes need a Home Assistant restart.
- Logs, entity states, and restarts go through the `home-assistant` MCP server (ha-mcp, HTTP on `10.19.0.34:9584`).
- The heat pump (Heliotherm WebControl/RCG) answers Modbus TCP on `10.19.0.70:502`, unit id 1.
