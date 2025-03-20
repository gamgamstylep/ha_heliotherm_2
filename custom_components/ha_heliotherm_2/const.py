"""Constants for the HaHeliotherm integration."""
import json
import os
from dataclasses import dataclass
from homeassistant.components.climate import (
    ClimateEntityDescription,
    ClimateEntityFeature,
)

from homeassistant.components.sensor import *

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberDeviceClass,
)

from homeassistant.components.lock import LockState
from homeassistant.components.alarm_control_panel import AlarmControlPanelState
from homeassistant.const import (
    UnitOfReactivePower,
    UnitOfArea,
    UnitOfConductivity,
    UnitOfTemperature,  # Add this line
    UnitOfPressure,  # Add this line
    UnitOfEnergy
    
)

DOMAIN = "ha_heliotherm2"
DEFAULT_NAME = "Heliotherm Heatpump2"
DEFAULT_SCAN_INTERVAL = 15
DEFAULT_PORT = 502
CONF_HELIOTHERM_HUB = "haheliotherm_hub"
ATTR_MANUFACTURER = "Heliotherm"
READING_REGISTER_FROM = 10
READING_REGISTER_TO = 99
DEFAULT_LANGUAGE = "de"
DEFAULT_ACCESS_MODE = "read_only"

CONF_ACCESS_MODE = "access_mode"  # Add this line
CONF_DISPLAY_LANGUAGE = "display_language"  # Add this line 

@dataclass
class HaHeliothermNumberEntityDescription(NumberEntityDescription):
    """A class that describes HaHeliotherm Modbus sensor entities."""

    mode: str = "slider"
    initial: float = None
    editable: bool = True


@dataclass
class HaHeliothermSensorEntityDescription(SensorEntityDescription):
    """A class that describes HaHeliotherm Modbus sensor entities."""
    # Removed register_number attribute


@dataclass
class HaHeliothermBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes HaHeliotherm Modbus binarysensor entities."""


@dataclass
class HaHeliothermSelectEntityDescription(SensorEntityDescription):
    """A class that describes HaHeliotherm Modbus binarysensor entities."""

    select_options: list[str] = None
    default_select_option: str = None
    setter_function = None


@dataclass
class HaHeliothermClimateEntityDescription(ClimateEntityDescription):
    """A class that describes HaHeliotherm Modbus binarysensor entities."""

    min_value: float = None
    max_value: float = None
    step: float = None
    register_number: int = None
    data_type: str = "uint16"
    hvac_modes: list[str] = None
    temperature_unit: str = "°C"
    supported_features: ClimateEntityFeature = ClimateEntityFeature.TARGET_TEMPERATURE