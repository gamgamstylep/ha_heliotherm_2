from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback
from .ha_heliotherm_base_entity import normalize_for_entity_id

NAMES = {"de": "Wärmepumpe erreichbar", "en": "Heat pump reachable"}


class HaHeliothermConnectivitySensor(BinarySensorEntity):
    """On while the heat pump answers Modbus requests, off otherwise."""

    _attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, platform_name, hub, device_info, display_language):
        self._hub = hub
        self._attr_device_info = device_info
        self._attr_name = f"{platform_name} {NAMES.get(display_language, NAMES['en'])}"
        self._attr_unique_id = normalize_for_entity_id(f"{platform_name}_modbus_reachable")

    async def async_added_to_hass(self):
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @property
    def is_on(self):
        return self._hub.available
