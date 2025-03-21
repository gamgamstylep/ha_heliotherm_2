import logging
from homeassistant.components.climate import ClimateEntity, HVACMode, ClimateEntityFeature
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from .ha_heliotherm_base_entity import HaHeliothermBaseEntity
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)
# https://developers.home-assistant.io/docs/core/entity/climate/
class HaHeliothermModbusClimate(HaHeliothermBaseEntity, ClimateEntity):
    """Representation of a Heliotherm Modbus climate entity."""

    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        register,
        register_key,
        display_language,
    ):
        super().__init__(platform_name, hub, device_info, register, register_key, display_language=display_language)
        self._hub_name = hub.name
        self._hub = hub
        self._device_info = device_info
        self._register = register
        self._register_key = register_key
        self._display_language = display_language
        self._state = None
        self._temperature = 20.0  # Default temperature, can be updated later.
        self._attr_temperature_unit = register['unit']
        #self._attr_min_temp = register['min']
        #self._attr_max_temp = register['max']
        self._attr_target_temperature_low = register['min']
        self._attr_target_temperature_high = register['max']
        self._attr_target_temperature_step = register['step']
        self._hvac_mode = HVACMode.AUTO  
        ###

    
    @property
    def hvac_mode(self):
        """Return the current HVAC mode."""
        return self._hvac_mode

    @property
    def hvac_modes(self):
        """Return the list of supported HVAC modes."""
        return [HVACMode.AUTO]
    
    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._temperature
      
    @property
    def target_temperature(self):
      """Return the target temperature."""
      return self._temperature  # Stelle sicher, dass dies die Solltemperatur ist.

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
        return self._register['min']  # Minimum temperature limit

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        return self._register['max']  # Maximum temperature limit

    @property
    def extra_state_attributes(self):
        """Return additional attributes for UI display."""
        return {
            "custom_status": "active",  # Example: extra attribute for UI
            "temperature_range": f"{self.min_temp}-{self.max_temp}°C"  # Use properties instead of attributes
        }
        
    # async def async_set_temperature(self, **kwargs):
    #     """Set the target temperature for the climate entity."""
    #     temperature = kwargs.get(ATTR_TEMPERATURE)
    #     if temperature is None:
    #         _LOGGER.warning("No temperature provided to set.")
    #         return
        
    #     if self.min_temp <= temperature <= self.max_temp:
    #         _LOGGER.debug(f"Setting temperature to {temperature}")
    #         self._temperature = temperature
    #         self.async_write_ha_state()
    #     else:
    #         _LOGGER.warning(f"Attempted to set out-of-range temperature: {temperature}")
    #         raise ValueError(
    #             f"Temperature {temperature} is out of range ({self.min_temp}-{self.max_temp})"
    #         )
            
    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        if "temperature" in kwargs:
            self._attr_current_temperature = float(kwargs["temperature"])
            self._attr_target_temperature = float(kwargs["temperature"])
        if "target_temp_low" in kwargs:
            self._attr_target_temperature_low = float(kwargs["target_temp_low"])
        if "target_temp_high" in kwargs:
            self._attr_target_temperature_high = float(kwargs["target_temp_high"])
        custom_data = {
            "register_key": self._register_key,
            "device_id": self.device_info.get("identifiers"),
        }
        self.hass.add_job(self._hub.setter_function_callback(self, kwargs, custom_data))
            

    # async def async_update(self):
    #     """Update the entity state by reading values from the device."""
    #     new_temperature = self._hub.data.get(self._register_key)
        
    #     if new_temperature is not None:
    #         self._temperature = new_temperature
    #         self.async_write_ha_state()
    #     else:
    #         _LOGGER.warning(f"No data found for key {self._register_key} in hub {self._hub_name}")

