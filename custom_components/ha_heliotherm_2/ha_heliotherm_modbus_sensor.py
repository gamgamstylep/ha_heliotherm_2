from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
# from pymodbus.payload import BinaryPayloadDecoder
# from pymodbus.constants import Endian
from homeassistant.core import callback
from .ha_heliotherm_base_entity import HaHeliothermBaseEntity
import logging
_LOGGER = logging.getLogger(__name__)
# def decode_uint32(value):
#     """Decode a UINT32 value from Modbus."""
#     decoder = BinaryPayloadDecoder.fromRegisters(value, byteorder=Endian.Big)
#     decoded_value = decoder.decode_32bit_uint()
#     return decoded_value

class HaHeliothermModbusSensor(HaHeliothermBaseEntity, SensorEntity):
    """Representation of an Heliotherm Modbus sensor."""
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.entity_id}={self.native_value}>"
      
    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        entity,
        entity_key,
        display_language,
        entity_specific_dict=None
    ):
        """Initialize the sensor."""
        super().__init__(platform_name, hub, device_info, entity, entity_key,display_language=display_language)
        if entity_specific_dict is None:
            entity_specific_dict = {}

        self._attr_native_unit_of_measurement = entity_specific_dict.get("native_unit_of_measurement", "")
        self._attr_device_class = entity_specific_dict.get("device_class", "")
        self._attr_state_class = entity_specific_dict.get("state_class", "")
        self.entity_description = SensorEntityDescription(
            key=entity_key,
            name=self.name,  # Corrected line
            device_class=self._attr_device_class,
            native_unit_of_measurement=self._attr_native_unit_of_measurement,
            state_class=self._attr_state_class,
        )
        #_LOGGER.debug(f"line44: entity_key: {entity_key}")
        #_LOGGER.debug(f"line44: self._name: {self._name}")
        
        self._attr_native_value = None

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        if self._entity_key in self._hub.data:
            self._attr_native_value = self._hub.data[self._entity_key]
        self.async_write_ha_state()


    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self._hub.data.get(self._entity_key)

        # Prüfen, ob die Einheit Promille (‰) ist und dann umrechnen
        if value is not None and self._entity.get("unit") == "‰":
            return value / 10  # Umwandlung von Promille in Prozent

        return value
