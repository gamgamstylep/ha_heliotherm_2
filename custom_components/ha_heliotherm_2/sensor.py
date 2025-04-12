from homeassistant.const import CONF_NAME, UnitOfTemperature, UnitOfPressure, UnitOfEnergy, UnitOfTime, UnitOfPower, UnitOfVolumeFlowRate

from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.components.input_number import *

import logging

import homeassistant.util.dt as dt_util

from .const import DOMAIN
from .ha_heliotherm_modbus_sensor import HaHeliothermModbusSensor
from .shared_setup import async_setup_shared

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
        "default": (UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING),
        "negative_energy": (UnitOfEnergy.KILO_WATT_HOUR, SensorDeviceClass.ENERGY, SensorStateClass.TOTAL),
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
    await async_setup_shared(
        hass,
        entry,
        async_add_entities,
        entity_type_key="entities_sensor",
        entity_class=HaHeliothermModbusSensor,
        unit_mapping=UNIT_MAPPING,
    )


