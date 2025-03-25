from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian
from homeassistant.core import callback
from .ha_heliotherm_base_entity import HaHeliothermBaseEntity

def decode_uint32(value):
    """Decode a UINT32 value from Modbus."""
    decoder = BinaryPayloadDecoder.fromRegisters(value, byteorder=Endian.Big)
    decoded_value = decoder.decode_32bit_uint()
    return decoded_value

class HaHeliothermModbusSensor(HaHeliothermBaseEntity, SensorEntity):
    """Representation of an Heliotherm Modbus sensor."""

    def __init__(
        self,
        platform_name,
        hub,
        device_info,
        register,
        register_key,
        display_language,
        native_unit_of_measurement,
        device_class,
        state_class,
    ):
        """Initialize the sensor."""
        super().__init__(platform_name, hub, device_info, register, register_key,display_language=display_language)
        self._attr_native_unit_of_measurement = native_unit_of_measurement
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self.entity_description = SensorEntityDescription(
            key=register_key,
            name=self.name,  # Corrected line
            device_class=device_class,
            native_unit_of_measurement=native_unit_of_measurement,
            state_class=state_class,
        )
    

    async def async_added_to_hass(self):
        """Register callbacks."""
        self._hub.async_add_haheliotherm_modbus_sensor(self._modbus_data_updated)

    async def async_will_remove_from_hass(self) -> None:
        self._hub.async_remove_haheliotherm_modbus_sensor(self._modbus_data_updated)

    @callback
    def _modbus_data_updated(self):
        if self._register_key in self._hub.data:
            self._attr_native_value = self._hub.data[self._register_key]
        self.async_write_ha_state()


    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self._hub.data.get(self._register_key)

        # Prüfen, ob die Einheit Promille (‰) ist und dann umrechnen
        if value is not None and self._register.get("unit") == "‰":
            return value / 10  # Umwandlung von Promille in Prozent

        return value
