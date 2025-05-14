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
        self._attr_entity_specific_dict = entity_specific_dict or {}
        
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
        if self._entity.get("combined_entity", False):
            return ClimateEntityFeature.TARGET_TEMPERATURE_RANGE
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

    def _update_from_hub_data(self):
        """Aktualisiere Entity-Zustände basierend auf Hub-Daten."""
        #_LOGGER.debug(f"Aktualisiere Daten für Entity-Key {self._entity_key} mit Hub-Daten: {self._hub.data}")
        
        if self._entity_key in self._hub.data:
            self._attr_current_temperature = self._hub.data[self._entity_key]
            self._attr_target_temperature = self._attr_current_temperature

        if self._entity.get("combined_entity", False):
            attributes_from_register = self._entity.get("attributes_from_register", {})
            # _LOGGER.debug(f"attributes_from_register: {attributes_from_register}")  
            target_temperature_low_entity_key = attributes_from_register.get("target_temperature_low")
            if target_temperature_low_entity_key and target_temperature_low_entity_key in self._hub.data:
                _LOGGER.debug(f"self._hub.data[target_temperature_low_entity_key]: {self._hub.data[target_temperature_low_entity_key]}") 
              
                self._attr_target_temperature_low = self._hub.data[target_temperature_low_entity_key]
                _LOGGER.debug(f"update_hub_data:self._attr_target_temperature_low: {self._attr_target_temperature_low}")
            target_temperature_high_entity_key = attributes_from_register.get("target_temperature_high")
            if target_temperature_high_entity_key and target_temperature_high_entity_key in self._hub.data:
                self._attr_target_temperature_high = self._hub.data[target_temperature_high_entity_key]
                _LOGGER.debug(f"update_hub_data:self._attr_target_temperature_high: {self._attr_target_temperature_high}")

        # 🟢 Jetzt neuen Zustand in der UI anzeigen
        self.async_write_ha_state()


        
    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        # Wann gebraucht? → Wenn der Benutzer in der UI eine neue Temperatur setzt.
        # Was macht sie? → Speichert den Wert lokal und löst über deinen Hub ein Setzen auf dem Modbus aus.
        _LOGGER.debug(f"Setting temperature to {kwargs}")
        if ATTR_TEMPERATURE in kwargs:
            self._attr_target_temperature = float(kwargs[ATTR_TEMPERATURE])
            self._attr_current_temperature = float(kwargs[ATTR_TEMPERATURE])
        if "target_temperature_low" in kwargs:
            _LOGGER.debug(f"Setting target temperature low to {kwargs['target_temperature_low']}")
            self._attr_target_temperature_low = float(kwargs["target_temperature_low"])
        if "target_temperature_high" in kwargs:
            self._attr_target_temperature_high = float(kwargs["target_temperature_high"])
        self.async_write_ha_state() # If a Modbus device sends updated temperature data, you would update the entity's internal state (e.g., `_attr_current_temperature`) and then call `async_write_ha_state` to reflect the changes in Home Assistant.
        
        custom_data = {
            "entity_key": self._entity_key,
            "device_id": self.device_info.get("identifiers"),
        }
        # setter_function_callback dann für beide temperature_low und temperature_high aufrufen - noch nicht implementiert ?
        self.hass.add_job(self._hub.setter_function_callback(self, kwargs, custom_data))
        

    async def async_update(self):
      """Update the entity state by reading values from the device."""
      self._update_from_hub_data()
      self.async_write_ha_state()

    @callback
    def _modbus_data_updated(self):
        """Handle updated data from Modbus."""
        #_LOGGER.debug(f"Modbus-Daten aktualisiert: {self._hub.data}")
        self._update_from_hub_data()
        self.async_write_ha_state()

            
    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self._hub.data.get(self._entity_key)
        if value is not None and self._entity.get("unit") == "‰":
            return value / 10  # Convert promille to percent
        return value
