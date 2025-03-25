from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode
from homeassistant.core import HomeAssistant

DOMAIN = "my_modbus_climate"

class ModbusClimate(ClimateEntity):
    """Modbus-based thermostat."""

    def __init__(self, hass: HomeAssistant, name: str, slave: int, temp_register: int, setpoint_register: int):
        """Initialize thermostat."""
        self.hass = hass
        self._attr_name = name
        self._slave = slave
        self._temp_register = temp_register
        self._setpoint_register = setpoint_register
        self._attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
        self._attr_hvac_mode = HVACMode.OFF
        self._attr_temperature = 20.0
        self._attr_target_temperature = 20.0

    def set_temperature(self, **kwargs):
        """Set the desired room temperature."""
        modbus_hub = self.hass.data.get("modbus").get("my_modbus")
        if modbus_hub:
            new_temp = kwargs.get("temperature")
            modbus_hub.write_register(slave=self._slave, address=self._setpoint_register, value=int(new_temp))
            self._attr_target_temperature = new_temp
            self.schedule_update_ha_state()

    def update(self):
        """Read current temperature from Modbus."""
        modbus_hub = self.hass.data.get("modbus").get("my_modbus")
        if modbus_hub:
            result = modbus_hub.read_registers(slave=self._slave, address=self._temp_register, count=1)
            if result:
                self._attr_temperature = result.registers[0]
