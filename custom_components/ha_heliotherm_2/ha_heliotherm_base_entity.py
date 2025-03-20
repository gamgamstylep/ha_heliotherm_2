from homeassistant.helpers.entity import Entity
from homeassistant.core import callback

class HaHeliothermBaseEntity: 
    """Base class for Heliotherm sensors."""

    def __init__(self, platform_name, hub, device_info, register, register_key, display_language):
        """Initialize the base sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self._hub = hub
        self._register = register
        self._register_key = register_key
        self._data_type = register["data_type"]
        self._display_language = display_language
        self._attr_name = f"{platform_name} {register['description'][self._display_language]}"
        self._name = self._attr_name  # Added line
        self._attr_unique_id = f"{platform_name}_{register_key}"
        self.entity_id = f"{register["type"]}.{platform_name}_{register_key}".lower()

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)
        
    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self._register['description'][self._display_language]}"

    @property
    def unique_id(self):
        return f"{self._platform_name}_{self._register_key}"
    
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            self._hub.data.get(self._register_key)
            if self._register_key in self._hub.data
            else None
        )
