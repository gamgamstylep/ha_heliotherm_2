from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import callback
from .ha_heliotherm_base_entity import HaHeliothermBaseEntity

class HeliothermSelect(HaHeliothermBaseEntity, SelectEntity):
    """Representation of a weenect select."""

    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        register,
        register_key,
        options: list[str],
        default_value: str,
        display_language,  # Add this line
    ):
        """Initialize the select entity."""
        super().__init__(platform_name, hub, device_info, register, register_key, display_language)  # Update this line
        self._attr_options = options
        self._attr_current_option = default_value
        self.entity_description = SelectEntityDescription(
            key=register_key,
            name=self.name,  # Corrected line
            options=options,
        )

    @property
    def current_option(self) -> str | None:
        """Return the selected entity option to represent the entity state."""
        return self._attr_current_option

    # async def async_select_option(self, option: str, register_key=None) -> None:
    #     """Change the selected option."""
    #     self._attr_current_option = option
    #     await self._hub.setter_function_callback(self, option, register_key)
        
    async def async_select_option(self, option: str) -> None:
        """Change the selected option and send additional data."""
        self._attr_current_option = option

        # Define custom data to send when the selection changes
        custom_data = {
            "register_key": self._register_key,
            "device_id": self.device_info.get("identifiers"),
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
        if self._register_key in self._hub.data:
            self._attr_current_option = self._hub.data[self._register_key]
        self.async_write_ha_state()
