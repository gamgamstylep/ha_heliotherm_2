from homeassistant.const import CONF_NAME
from homeassistant.components.input_number import *

import logging
from typing import Optional, Dict, Any

import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .ha_heliotherm_modbus_sensor import HaHeliothermModbusSensor
from .ha_heliotherm_modbus_binary_sensor import HaHeliothermModbusBinarySensor
from .ha_heliotherm_select import HeliothermSelect
from .ha_heliotherm_modbus_climate import HaHeliothermModbusClimate  # Add this import

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]
    wpRegisters = hass.data[DOMAIN]["wp_registers_binary_sensor"]
    wp_config = hass.data[DOMAIN]["wp_config"]
    display_language = entry.data.get("display_language", "en")

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": wp_config["manufacturer"],
    }
    entities = []
    added_entities = set()  # Track added entities to avoid duplicates

    for register_key, register in wpRegisters.items():
        if "omit" in register:
          if register["omit"] == True:
              continue
        if register["register_number"] > wp_config["register_number_read_max"]:
            break  # Skip if register number is too high
        if register_key in added_entities:
            continue  # Skip if already added
        sensor = None
        #_LOGGER.debug(f"Registerkey: {register_key} Registertype: {register['type']}")
        sensor = HaHeliothermModbusBinarySensor(
            hub_name,
            hub,
            device_info,
            register,
            register_key=register_key,
            display_language=display_language,
        )
        sensor._attr_name = sensor.name  # Ensure name is set
        if sensor is not None:
          entities.append(sensor)
          #_LOGGER.debug(f"Added entity: {sensor}")
          added_entities.add(register_key)  # Mark as added
    if "added_entities" in hass.data[DOMAIN][hub_name]:
      added_entities.update(hass.data[DOMAIN][hub_name]["added_entities"])
    hass.data[DOMAIN][hub_name]["added_entities"] = added_entities
    async_add_entities(entities)
    return True


