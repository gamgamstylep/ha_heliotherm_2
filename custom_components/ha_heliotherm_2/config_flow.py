"""Config flow for HaHeliotherm integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, DEFAULT_NAME, DEFAULT_PORT

_LOGGER = logging.getLogger(__name__)

# New constant for display language
CONF_DISPLAY_LANGUAGE = "display_language"
LANGUAGES = {
    "en": "English",
    "de": "German",
}
DEFAULT_LANGUAGE = "de"

# Existing constants
CONF_ACCESS_MODE = "access_mode"
ACCESS_MODES = {
    "read_only": "Read Only",
    "read_write": "Read/Write",
}
DEFAULT_ACCESS_MODE = "read_only"

def host_valid(host: str) -> bool:
    """Return True if hostname or IP address is valid."""
    import ipaddress
    import re
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        if re.match(r"^(?!-)[A-Za-z\d-]{1,63}(?<!-)(\.[A-Za-z\d-]{1,63})*$", host):
            return True
    _LOGGER.warning("Invalid host format: %s", host)
    return False


@callback
def ha_heliotherm_modbus_entries(hass: HomeAssistant):
    """Return the hosts already configured."""
    return set(
        entry.data[CONF_HOST] for entry in hass.config_entries.async_entries(DOMAIN)
    )

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HaHeliotherm."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def _host_in_configuration_exists(self, host) -> bool:
        """Return True if host exists in configuration."""
        return host in ha_heliotherm_modbus_entries(self.hass)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        import homeassistant.helpers.config_validation as cv
        import voluptuous as vol

        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            if self._host_in_configuration_exists(host):
                errors[CONF_HOST] = "already_configured"
            elif not host_valid(user_input[CONF_HOST]):
                errors[CONF_HOST] = "invalid host or IP"
            else:
                await self.async_set_unique_id(user_input[CONF_HOST])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_PORT, default=DEFAULT_PORT): cv.string,
                vol.Required(CONF_ACCESS_MODE, default="read_only"): vol.In(ACCESS_MODES),
                vol.Required(CONF_DISPLAY_LANGUAGE, default=DEFAULT_LANGUAGE): vol.In(LANGUAGES),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry  # This line will be removed or handled differently in the future

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        import homeassistant.helpers.config_validation as cv
        import voluptuous as vol

        if user_input is not None:
            user_input[CONF_NAME] = self.config_entry.data[CONF_NAME]
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=self.config_entry.data[CONF_HOST]): cv.string,
                    vol.Required(CONF_PORT, default=self.config_entry.data[CONF_PORT]): cv.string,
                    vol.Required(
                        CONF_ACCESS_MODE,
                        default=self.config_entry.data.get(CONF_ACCESS_MODE, DEFAULT_ACCESS_MODE)
                    ): vol.In(ACCESS_MODES),
                    vol.Required(
                        CONF_DISPLAY_LANGUAGE,
                        default=self.config_entry.data.get(CONF_DISPLAY_LANGUAGE, DEFAULT_LANGUAGE)
                    ): vol.In(LANGUAGES),
                }
            ),
        )

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        import homeassistant.helpers.config_validation as cv
        import voluptuous as vol

        if user_input is not None:
            user_input[CONF_NAME] = self.config_entry.data[CONF_NAME]
            self.hass.config_entries.async_update_entry(
                self.config_entry, data={**self.config_entry.data, **user_input}
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data={})

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=self.config_entry.data[CONF_HOST]): cv.string,
                    vol.Required(CONF_PORT, default=self.config_entry.data[CONF_PORT]): cv.string,
                    vol.Required(
                        CONF_ACCESS_MODE,
                        default=self.config_entry.data.get(CONF_ACCESS_MODE, DEFAULT_ACCESS_MODE)
                    ): vol.In(ACCESS_MODES),
                    vol.Required(
                        CONF_DISPLAY_LANGUAGE,
                        default=self.config_entry.data.get(CONF_DISPLAY_LANGUAGE, DEFAULT_LANGUAGE)
                    ): vol.In(LANGUAGES),
                }
            ),
        )
