from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import callback
from .ha_heliotherm_base_entity import HaHeliothermBaseEntity

class HaHeliothermModbusBinarySensor(HaHeliothermBaseEntity, BinarySensorEntity):
    """Representation of an Heliotherm Modbus binary sensor."""

    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        entity,
        entity_key,
        display_language,
        entity_specific_dict=None,
    ):
        """Initialize the binary sensor."""
        super().__init__(platform_name, hub, device_info, entity, entity_key,display_language)

    @callback
    def _update_state(self):
        if self._entity_key in self._hub.data:
            self._attr_is_on = self._hub.data[self._entity_key] == "on"

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return (
            self._hub.data[self._entity_key]
            if self._entity_key in self._hub.data
            else None
        )
