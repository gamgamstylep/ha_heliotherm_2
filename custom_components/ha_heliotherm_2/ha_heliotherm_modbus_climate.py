import logging
from homeassistant.components.climate import (
    ClimateEntity, HVACMode, ClimateEntityFeature, ClimateEntityDescription
)
from homeassistant.const import ATTR_TEMPERATURE
from homeassistant.core import callback
from .ha_heliotherm_base_entity import HaHeliothermBaseEntity

_LOGGER = logging.getLogger(__name__)

class HaHeliothermModbusClimate(HaHeliothermBaseEntity, ClimateEntity):
    """Representation of a Heliotherm Modbus climate entity."""

    def __init__(self, platform_name, hub, device_info, entity, entity_key, display_language,entity_specific_dict=None):
        super().__init__(platform_name, hub, device_info, entity, entity_key, display_language)
        self._hub = hub
        self._entity = entity
        self._entity_key = entity_key
        self._display_language = display_language
        self._attr_temperature_unit = entity['unit']
        self._attr_target_temperature_low = entity['min']
        self._attr_target_temperature_high = entity['max']
        self._attr_target_temperature_step = entity['step']
        self._attr_hvac_mode = HVACMode.AUTO  
        self._attr_current_temperature = None
        self._attr_target_temperature = None
        
        self.entity_description = ClimateEntityDescription(
            key=entity_key,
            name=self.name
        )
    
    @property
    def hvac_mode(self):
        """Return the current HVAC mode."""
        return self._attr_hvac_mode

    @property
    def hvac_modes(self):
        """Return the list of supported HVAC modes."""
        return [HVACMode.AUTO]
    
    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._attr_current_temperature
      
    @property
    def target_temperature(self):
        """Return the target temperature."""
        return self._attr_target_temperature

    @property
    def temperature_unit(self):
        """Return the temperature unit."""
        return self._attr_temperature_unit

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return ClimateEntityFeature.TARGET_TEMPERATURE

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        return self._entity['min']

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._entity['max']

    @property
    def extra_state_attributes(self):
        """Return additional attributes for UI display."""
        return {
            "custom_status": "active",
            "temperature_range": f"{self.min_temp}-{self.max_temp}°C"
        }
        
    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        _LOGGER.debug(f"Setting temperature to {kwargs}")
        if ATTR_TEMPERATURE in kwargs:
            self._attr_target_temperature = float(kwargs[ATTR_TEMPERATURE])
            self._attr_current_temperature = float(kwargs[ATTR_TEMPERATURE])
        if "target_temp_low" in kwargs:
            self._attr_target_temperature_low = float(kwargs["target_temp_low"])
        if "target_temp_high" in kwargs:
            self._attr_target_temperature_high = float(kwargs["target_temp_high"])
        
        self.async_write_ha_state()
        
        custom_data = {
            "entity_key": self._entity_key,
            "device_id": self.device_info.get("identifiers"),
        }
        self.hass.add_job(self._hub.setter_function_callback(self, kwargs, custom_data))

    async def async_update(self):
        """Update the entity state by reading values from the device."""
        new_temperature = self._hub.data.get(self._entity_key)
        
        if new_temperature is not None:
            self._attr_current_temperature = new_temperature
            self.async_write_ha_state()
        else:
            _LOGGER.debug(f"No data found for key {self._entity_key} in hub {self._hub.name}")
            
    @callback
    def _modbus_data_updated(self):
        """Handle updated data from Modbus."""
        if self._entity_key in self._hub.data:
            self._attr_current_temperature = self._hub.data[self._entity_key]
            self._attr_target_temperature = self._attr_current_temperature
        self.async_write_ha_state()
            
    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self._hub.data.get(self._entity_key)
        if value is not None and self._entity.get("unit") == "‰":
            return value / 10  # Convert promille to percent
        return value
