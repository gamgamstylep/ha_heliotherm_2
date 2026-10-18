from homeassistant.const import CONF_NAME
from homeassistant.components.input_number import *

import logging
from .const import DOMAIN
from .shared_setup import async_setup_shared
from .ha_heliotherm_modbus_binary_sensor import HaHeliothermModbusBinarySensor
from .ha_heliotherm_connectivity_sensor import HaHeliothermConnectivitySensor


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    await async_setup_shared(
        hass,
        entry,
        async_add_entities,
        entity_type_key="entities_binary_sensor",
        entity_class=HaHeliothermModbusBinarySensor,
    )
    hub_name = entry.data[CONF_NAME]
    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": hass.data[DOMAIN]["wp_config"]["manufacturer"],
    }
    async_add_entities([
        HaHeliothermConnectivitySensor(
            hub_name,
            hass.data[DOMAIN][hub_name]["hub"],
            device_info,
            entry.data.get("display_language", "en"),
        )
    ])


