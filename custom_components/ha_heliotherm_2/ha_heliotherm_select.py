from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import callback
from .ha_heliotherm_base_entity import HaHeliothermBaseEntity
import logging
_LOGGER = logging.getLogger(__name__)
class HeliothermSelect(HaHeliothermBaseEntity, SelectEntity):
    """Representation of a weenect select."""

    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        entity,
        entity_key,
        display_language,  # Add this line
        entity_specific_dict=None
    ):
        """Initialize the select entity."""
        super().__init__(platform_name, hub, device_info, entity, entity_key, display_language)  # Update this line
        self._attr_options = list(entity["options"].values()) if "options" in entity else None
        self._attr_current_option = entity.get("default_option")
        self.entity_description = SelectEntityDescription(
            key=entity_key,
            name=self.name, 
            options=self._attr_options,
        )
    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self._attr_current_option
        
    async def async_select_option(self, option: str) -> None:
        """Change the selected option and send additional data."""
        self._attr_current_option = option

        # Define custom data to send when the selection changes
        custom_data = {
            "entity_key": self._entity_key,
            "device_id": self.device_info.get("identifiers"),
            "entity": self._entity
        }

        # Call the hub function with extra data
        await self._hub.setter_function_callback(self, option, custom_data)

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        if self._entity_key in self._hub.data:
            self._attr_current_option = self._hub.data[self._entity_key]
        self.async_write_ha_state()
