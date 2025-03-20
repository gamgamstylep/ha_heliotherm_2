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
    # native_unit_of_measurement, device_class, state_class
    "°C": (UnitOfTemperature.CELSIUS, SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT),
    "bar": (UnitOfPressure.BAR, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    "mbar": (UnitOfPressure.BAR, SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    "kW/h": (UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
    "h": (UnitOfTime.HOURS, None, SensorStateClass.MEASUREMENT),
    "W": (UnitOfPower.WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    "kW": (UnitOfPower.KILO_WATT, SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT),
    "l/min": (UnitOfVolumeFlowRate.LITERS_PER_MINUTE, SensorDeviceClass.VOLUME_FLOW_RATE, SensorStateClass.MEASUREMENT),
    "‰": ("‰", SensorDeviceClass.PRESSURE, SensorStateClass.MEASUREMENT),
    "number": (None, None, None),
    "%": (None, None, None),
}

async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]
    wpRegisters = hass.data[DOMAIN]["wp_registers"]
    wp_config = hass.data[DOMAIN]["wp_config"]
    wpCombinedSensors = hass.data[DOMAIN]["wp_combined_sensors"]
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
        _LOGGER.debug(f"Registerkey: {register_key} Registertype: {register['type']}")
        if register["type"] == "sensor":
            native_unit_of_measurement, device_class, state_class = UNIT_MAPPING.get(
                register["unit"], (None, None, None)
            )
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
        elif register["type"] == "binary":
            sensor = HaHeliothermModbusBinarySensor(
                hub_name,
                hub,
                device_info,
                register,
                register_key=register_key,
                display_language=display_language,
            )
        elif register["type"] == "climate":
            sensor = HaHeliothermModbusClimate(
                hub_name,
                hub,
                device_info,
                register,
                register_key=register_key,
                display_language=display_language,
            )
            _LOGGER.debug(f"Climate: {sensor}")
        elif register["type"] == "select":
            #_LOGGER.debug(f"Register: {register}")
            options = list(register["options"].values()) if "options" in register else None
            default_key = register.get("default_option")
            default_value = register["options"].get(str(default_key)) if options and default_key is not None else None
            sensor = HeliothermSelect(
                hub_name,
                hub,
                device_info,
                register,
                register_key=register_key,
                options=options,
                default_value=default_value,
                display_language=display_language,
            )
        else:
            continue  # Skip unknown types

        sensor._attr_name = sensor.name  # Ensure name is set
        if sensor is not None:
          entities.append(sensor)
          #_LOGGER.debug(f"Added entity: {sensor}")
          added_entities.add(register_key)  # Mark as added
          
# If you want to specifically check if an entity is an instance of ClimateEntity:
    _LOGGER.debug(f"Entities to add: {[f'{e.__class__.__name__} ({e.entity_id})' for e in entities]}")
# Manually forward each entity type to its correct platform
    # Check if the entity is an instance of any specific entity class
    # for entity in entities:
    #     if isinstance(entity, SensorEntity):
    #         _LOGGER.debug(f"Entity {entity.entity_id} is a SensorEntity")
    #     elif isinstance(entity, ClimateEntity):
    #         _LOGGER.debug(f"Entity {entity.entity_id} is a ClimateEntity")
    #     elif isinstance(entity, BinarySensorEntity):
    #         _LOGGER.debug(f"Entity {entity.entity_id} is a BinarySensorEntity")
    #     elif isinstance(entity, SelectEntity):
    #         _LOGGER.debug(f"Entity {entity.entity_id} is a SelectEntity")
    #     else:
    #         _LOGGER.debug(f"Entity {entity.entity_id} is not a known entity type")
    # async_add_entities(entities)
    hass.data[DOMAIN][hub_name]["added_entities"] = added_entities
    return True


