from homeassistant.const import CONF_NAME
from homeassistant.components.input_number import *

import logging
from .const import DOMAIN
from .shared_setup import async_setup_shared
from .ha_heliotherm_modbus_binary_sensor import HaHeliothermModbusBinarySensor


_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    await async_setup_shared(
        hass,
        entry,
        async_add_entities,
        entity_type_key="entities_binary_sensor",
        entity_class=HaHeliothermModbusBinarySensor,
    )


