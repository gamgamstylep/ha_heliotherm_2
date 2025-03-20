from homeassistant.const import CONF_NAME, UnitOfTemperature, UnitOfPressure, UnitOfEnergy, UnitOfTime, UnitOfPower, UnitOfVolumeFlowRate
from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.components.input_number import *
from homeassistant.components.climate import (
    ClimateEntityDescription,
    ClimateEntityFeature,
    ClimateEntity,
)
from homeassistant.components.select import SelectEntity
import logging
from typing import Optional, Dict, Any

import homeassistant.util.dt as dt_util

from .const import DOMAIN, CONF_DISPLAY_LANGUAGE
from .ha_heliotherm_modbus_sensor import HaHeliothermModbusSensor
from .ha_heliotherm_modbus_binary_sensor import HaHeliothermModbusBinarySensor
from .ha_heliotherm_select import HeliothermSelect
from .ha_heliotherm_modbus_climate import HaHeliothermModbusClimate  # Add this import

_LOGGER = logging.getLogger(__name__)

UNIT_MAPPING = {
    "°C": {
        "default": (UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT)
    },
    "bar": {
        "default": (UnitOfPressure.BAR, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT)
    },
    "mbar": {
        "default": (UnitOfPressure.BAR, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT)
    },
    "kW/h": {
        "default": (UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING)
    },
    "h": {
        "default": (UnitOfTime.HOURS, None, SensorStateClass.MEASUREMENT)
    },
    "W": {
        "default": (UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT)
    },
    "kW": {
        "default": (UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT)
    },
    "l/min": {
        "default": (UnitOfVolumeFlowRate.LITERS_PER_MINUTE, SensorDeviceClass.VOLUME_FLOW_RATE, SensorStateClass.MEASUREMENT)
    },
    "‰": {
        "default": ("%", SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
        "speed": ("%", None, None)
    },
    "number": {
        "default": (None, None, None)
    },
    "%": {
        "default": ("%", None, None),
        "speed": ("%", None, None)
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]
    wpRegisters = hass.data[DOMAIN]["wp_registers_sensor"]
    wp_config = hass.data[DOMAIN]["wp_config"]
    display_language = entry.data.get(CONF_DISPLAY_LANGUAGE, "en")

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
        my_unit = register["unit"]
        my_device_class = register.get("device_class", "default")  # Default to "default" if not present

        # Determine the appropriate context
        unit_mapping = UNIT_MAPPING.get(my_unit, {})
        context = my_device_class if my_device_class in unit_mapping else "default"

        # Retrieve the mapping values
        native_unit_of_measurement, device_class, state_class = unit_mapping.get(context, (None, None, None))
        sensor = HaHeliothermModbusSensor(
            hub_name,
            hub,
            device_info,
            register,
            register_key=register_key,
            display_language=display_language,
            native_unit_of_measurement=native_unit_of_measurement,
            device_class=device_class,
            state_class=state_class,
        )
        sensor._attr_name = sensor.name  # Ensure name is set
        if sensor is not None:
          entities.append(sensor)
          #_LOGGER.debug(f"Added entity: {sensor}")
          added_entities.add(register_key)  # Mark as added
          
# If you want to specifically check if an entity is an instance of ClimateEntity:
    _LOGGER.debug(f"Entities to add: {[f'{e.__class__.__name__} ({e.entity_id})' for e in entities]}")

    if "added_entities" in hass.data[DOMAIN][hub_name]:
      added_entities.update(hass.data[DOMAIN][hub_name]["added_entities"])
    hass.data[DOMAIN][hub_name]["added_entities"] = added_entities
    async_add_entities(entities)
    return True


