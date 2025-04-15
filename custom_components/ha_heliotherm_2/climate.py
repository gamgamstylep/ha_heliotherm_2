# https://developers.home-assistant.io/docs/core/entity/climate/
from homeassistant.const import CONF_NAME
from homeassistant.components.input_number import *
import logging
from .const import DOMAIN
from .ha_heliotherm_modbus_climate import HaHeliothermModbusClimate
from .shared_setup import async_setup_shared

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    await async_setup_shared(
        hass,
        entry,
        async_add_entities,
        entity_type_key="entities_climate",
        entity_class=HaHeliothermModbusClimate,
    )
    await async_setup_shared(
        hass,
        entry,
        async_add_entities,
        entity_type_key="entities_climate_combined",
        entity_class=HaHeliothermModbusClimate,
    )
