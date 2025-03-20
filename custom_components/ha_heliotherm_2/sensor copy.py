from homeassistant.const import CONF_NAME, UnitOfTemperature, UnitOfPressure, UnitOfEnergy, UnitOfTime, UnitOfPower  # Add this import
from homeassistant.core import callback
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass  # Fix import
from homeassistant.components.input_number import *
from homeassistant.components.climate import (
    ClimateEntityDescription,
    ClimateEntityFeature,
)
import logging
from typing import Optional, Dict, Any

import homeassistant.util.dt as dt_util

from .const import (
    DOMAIN,
)
from .ha_heliotherm_modbus_sensor import HaHeliothermModbusSensor
from .ha_heliotherm_modbus_binary_sensor import HaHeliothermModbusBinarySensor
from .ha_heliotherm_select import HeliothermSelect  # Add this import

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    hub_name = entry.data[CONF_NAME]
    hub = hass.data[DOMAIN][hub_name]["hub"]
    haRegisters = hass.data[DOMAIN]["haRegisters"]
    wp_config = hass.data[DOMAIN]["config"]
    combinedSensors = hass.data[DOMAIN]["combinedSensors"] 

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": wp_config["manufacturer"],
    }
    entities = []
    added_entities = set()  # Track added entities to avoid duplicates

    for register_key, register in haRegisters.items():  # Iterate over items to get key and value
        _LOGGER.debug(f"Registerkey: {register_key}")
        if register_key in added_entities:
            continue  # Skip if already added
        if register["type"] == "sensor":
                if register["unit"] == "°C":
                    native_unit_of_measurement = UnitOfTemperature.CELSIUS
                    device_class = SensorDeviceClass.TEMPERATURE
                    state_class = SensorStateClass.MEASUREMENT
                elif register["unit"] == "bar":
                    native_unit_of_measurement = UnitOfPressure.BAR
                    device_class=SensorDeviceClass.PRESSURE,
                    state_class = SensorStateClass.MEASUREMENT
                elif register["unit"] == "kW/h":
                    native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR
                    device_class=SensorDeviceClass.ENERGY
                    state_class=SensorStateClass.TOTAL_INCREASING
                elif register["unit"] == "h":
                    native_unit_of_measurement=UnitOfTime.HOURS
                    device_class=SensorDeviceClass.TIMESTAMP
                    state_class=SensorStateClass.MEASUREMENT
                elif register["unit"] == "W":
                    native_unit_of_measurement=UnitOfPower.WATT
                    device_class=SensorDeviceClass.POWER
                    state_class=SensorStateClass.MEASUREMENT
                elif register["unit"] == "kW":
                    native_unit_of_measurement=UnitOfPower.KILO_WATT
                    device_class=SensorDeviceClass.POWER
                    state_class=SensorStateClass.MEASUREMENT
                else:
                    native_unit_of_measurement = None
                    device_class = None
                    state_class = None
                sensor = HaHeliothermModbusSensor(
                    hub_name,
                    hub,
                    device_info,
                    register,
                    register_key=register_key,
                    native_unit_of_measurement=native_unit_of_measurement,
                    device_class=device_class,
                    state_class=state_class,
                )
                entities.append(sensor)
                added_entities.add(register_key)  # Mark as added
        elif register["type"] == "binary":
                sensor = HaHeliothermModbusBinarySensor(
                    hub_name,
                    hub,
                    device_info,
                    register,
                    register_key=register_key,
                )
                entities.append(sensor)
                added_entities.add(register_key)  # Mark as added
        elif register["type"] == "select":
            options = list(register["options"].values()) if "options" in register else None  # Set options to None if not present
            default_key = register["default_select_option"]  # Extract the default key
            default_value = register["options"].get(default_key) if options else None  # Get the value for the default key if options exist
            sensor = HeliothermSelect(
                  hub_name,
                  hub,
                  device_info,
                  register,
                  register_key=register_key,
                  options = options,  # Pass the extracted values or None
                  default_value = default_value,  # Pass the default value or None
            )
            entities.append(sensor)
            added_entities.add(register_key)  # Mark as added

    for sensor in combinedSensors:
        if sensor.unique_id not in added_entities:
            entities.append(sensor)
            added_entities.add(sensor.unique_id)  # Mark as added

    async_add_entities(entities)
    return True

