from homeassistant.core import callback

import unicodedata
import re

def normalize_for_entity_id(text: str) -> str:
    # Entfernt Umlaute, Sonderzeichen & Leerzeichen
    # Beispiel: "wärmepumpe test" → "waermepumpe_test"
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")  # ä → ae etc.
    text = re.sub(r"[^a-zA-Z0-9_]+", "_", text)            # alles nicht erlaubte ersetzen
    text = re.sub(r"_+", "_", text)                        # doppelte _ vermeiden
    return text.lower().strip("_")


class HaHeliothermBaseEntity:
    """Base class for Heliotherm sensors."""

    def __init__(self, platform_name, hub, device_info, entity, entity_key, display_language):
        """Initialize the base sensor."""
        self._platform_name = platform_name
        self._attr_device_info = device_info
        self._hub = hub
        self._entity = entity
        self._entity_key = entity_key
        self._data_type = entity["data_type"]
        self._display_language = display_language

        # Benutzerfreundlicher Name (darf ä, ö, ü enthalten)
        display_name = f"{platform_name} {entity['description'][self._display_language]}"
        self._attr_name = display_name

        # Stabiler technischer Identifier ohne Sonderzeichen
        unique_name = normalize_for_entity_id(f"{platform_name}_{entity_key}")
        self._attr_unique_id = unique_name


    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)
        
    @callback
    def _modbus_data_updated(self):
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Unavailable while the heat pump does not answer Modbus requests."""
        return self._hub.available

    @property
    def name(self):
        """Return the name."""
        return f"{self._platform_name} {self._entity['description'][self._display_language]}"

    @property
    def unique_id(self):
        return getattr(self, "_attr_unique_id", None)
    
    @property
    def native_value(self):
        """Return the state of the sensor."""
        return (
            self._hub.data.get(self._entity_key)
            if self._entity_key in self._hub.data
            else None
        )
