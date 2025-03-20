"""The HaHeliotherm integration."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import threading
from typing import Optional
import json
import aiofiles
import os
import logging

# Get the logger for your custom component (use your component's name)
_LOGGER = logging.getLogger(__name__)

from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder
import voluptuous as vol

from homeassistant.helpers.entity import Entity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
    Platform,
)
from homeassistant.core import HomeAssistant, callback, ServiceCall
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.components.lock import LockState
from homeassistant.components.alarm_control_panel import AlarmControlPanelState
from homeassistant.const import UnitOfReactivePower, UnitOfArea, UnitOfConductivity

# Bestimme den Pfad zur JSON-Datei relativ zur __init__.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, "heliotherm_config.json")


from .const import DEFAULT_NAME, DEFAULT_SCAN_INTERVAL, DOMAIN, CONF_ACCESS_MODE, CONF_DISPLAY_LANGUAGE


# PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.SELECT]
#PLATFORMS = [Platform.SELECT, Platform.SENSOR, Platform.BINARY_SENSOR, Platform.CLIMATE]

config_file_path = JSON_PATH

# Store the loaded config data (None initially)
wp_json_config_data = None

# Async function to load the JSON config file once
async def load_config_once():
    """Load the JSON config file asynchronously, only once."""
    global wp_json_config_data

    if wp_json_config_data is None:  # Check if wp_json_config_data is already loaded
        if os.path.exists(config_file_path):
            async with aiofiles.open(config_file_path, 'r') as f:
                content = await f.read()
                wp_json_config_data = json.loads(content)  # Load config data only once
        else:
            wp_json_config_data = {}

    return wp_json_config_data

async def async_setup(hass, config):
    """Set up the HaHeliotherm modbus component."""
    hass.data[DOMAIN] = {}
    """Set up the custom component."""
    # Load configuration asynchronously (only once)
    wp_json_config_data = await load_config_once()
    access_mode = hass.data[DOMAIN]["wp_config_access_mode"] if "wp_config_access_mode" in hass.data[DOMAIN] else "read_only"

    # Store the configuration data in hass.data for other components or entities to access
    filtered_registers = {k: v for k, v in wp_json_config_data["registers"].items() if not v.get("omit", False)}
    sensor_registers = {k: v for k, v in filtered_registers.items() if v["type"] == "sensor"}
    binary_sensor_registers = {k: v for k, v in filtered_registers.items() if v["type"] == "binary"}  
    climate_registers = {k: v for k, v in filtered_registers.items() if v["type"] == "climate"}
    select_registers = {k: v for k, v in filtered_registers.items() if v["type"] == "select"}
    hass.data[DOMAIN]["wp_registers_sensor"] = sensor_registers
    hass.data[DOMAIN]["wp_registers_binary_sensor"] = binary_sensor_registers
    hass.data[DOMAIN]["wp_registers_climate"] = climate_registers
    hass.data[DOMAIN]["wp_registers_select"] = select_registers
    hass.data[DOMAIN]["wp_registers"] = filtered_registers
    hass.data[DOMAIN]["wp_config"] = wp_json_config_data["config"]
    hass.data[DOMAIN]["wp_combined_sensors"] = wp_json_config_data["combined_sensors"]
    config_wp_registers = hass.data[DOMAIN]["wp_registers"]
    wp_config = hass.data[DOMAIN]["wp_config"]
    async def set_room_temperature_service(call):
        """Handle setting the room temperature using the heat pump."""
        device_id = call.data.get("device_id")
        temperature = call.data.get("temperature")
        
        _LOGGER.info(f"Setting room temperature of device {device_id} to {temperature}°C")
        
        # Retrieve the heat pump device entity by device_id
        entity = hass.states.get(f"climate.{device_id}")
        
        if entity:
            # Call the async_set_temperature method on the entity
            await entity.async_set_temperature(temperature)
            _LOGGER.info(f"Room temperature set to {temperature}°C")
        else:
            _LOGGER.error(f"Device {device_id} not found")

    # Register the service with Home Assistant
    hass.services.async_register(DOMAIN, "set_room_temperature", set_room_temperature_service)
    
    async def handle_write_register(call: ServiceCall):
        """Handle writing to the holding register."""
        address = call.data.get('address')
        value = call.data.get('value')
        
        modbus_client = hass.data.get('modbus_tcp')
        if access_mode != "read_only":
          if modbus_client:
              _LOGGER.info(f"Writing {value} to register {address}")
              result = await modbus_client.write_register(address, value)
              if result:
                  _LOGGER.info(f"Successfully wrote {value} to register {address}")
              else:
                  _LOGGER.error(f"Failed to write to register {address}")
          else:
              _LOGGER.error("Modbus client is not available.")
    
    hass.services.async_register(DOMAIN, "write_register", handle_write_register)

    return True


    # Example: Logging the loaded config (you can replace this with actual entity setup)
    #_LOGGER.debug(f"Loaded configuration: {wp_json_config_data}")  # Update this line
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up a HaHeliotherm modbus."""
    host = entry.data[CONF_HOST]
    name = entry.data[CONF_NAME]
    port = entry.data[CONF_PORT]
    access_mode = entry.data.get(CONF_ACCESS_MODE, "read_only")
    hass.data[DOMAIN]["wp_config_access_mode"] = access_mode  
    display_language = entry.data.get(CONF_DISPLAY_LANGUAGE, "en") 
    scan_interval = DEFAULT_SCAN_INTERVAL

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = HaHeliothermModbusHub(hass, name, host, port, scan_interval, access_mode, display_language)
    # """Register the hub."""
    hass.data[DOMAIN][name] = {"hub": hub}
    # await hass.config_entries.async_forward_entry_setup(entry, "sensor")  # old
    #await hass.config_entries.async_forward_entry_setups(entry, ["sensor"]) # new
    #await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "climate"])
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "climate", "select"])
    return True

async def async_unload_entry(hass, entry):
    """Unload HaHeliotherm mobus entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if not unload_ok:
        return False

    hass.data[DOMAIN].pop(entry.data["name"])
    return True

class HaHeliothermModbusHub:
    """Thread safe wrapper class for pymodbus."""

    def __init__(
        self,
        hass: HomeAssistant,
        name,
        host,
        port,
        scan_interval,
        access_mode,
        display_language,
    ):
        """Initialize the Modbus hub."""
        self._hass = hass
        self._client = ModbusTcpClient(
            host=host, port=port, timeout=3, retries=3
        )
        self._lock = threading.Lock()
        self._name = name
        self._scan_interval = timedelta(seconds=scan_interval)
        self._access_mode = access_mode
        self._display_language = display_language
        self._unsub_interval_method = None
        self._sensors = []
        self.data = {}

    @callback
    def async_add_haheliotherm_modbus_sensor(self, update_callback):
        """Listen for data updates."""
        # This is the first sensor, set up interval.
        if not self._sensors:
            self.connect()
            self._unsub_interval_method = async_track_time_interval(
                self._hass, self.async_refresh_modbus_data, self._scan_interval
            )

        self._sensors.append(update_callback)

    @callback
    def async_remove_haheliotherm_modbus_sensor(self, update_callback):
        """Remove data update."""
        self._sensors.remove(update_callback)

        if not self._sensors:
            # """stop the interval timer upon removal of last sensor"""
            self._unsub_interval_method()
            self._unsub_interval_method = None
            self.close()

    async def async_refresh_modbus_data(self, _now: Optional[int] = None) -> None:
        """Time to update."""
        if not self._sensors:
            return
        _LOGGER.debug("Updating modbus data")
        update_result = self.read_modbus_registers()

        if update_result:
            for update_callback in self._sensors:
                update_callback()

    @property
    def name(self):
        """Return the name of this hub."""
        return self._name

    def close(self):
        """Disconnect client."""
        with self._lock:
            self._client.close()

    def connect(self):
        """Connect client."""
        with self._lock:
            self._client.connect()
            
    def read_modbus_registers(self):
        """Read from modbus registers"""
        wp_config = self._hass.data[DOMAIN]["wp_config"]
        reading_registers = wp_config["reading_registers"]
        #_LOGGER.debug(f"Reading registers: {reading_registers}")
        modbusdata_input_registers_values = {}
        for register_read in reading_registers:
            #_LOGGER.debug(f"Reading register: {register_read}")
            start_address = register_read["start_address"]
            count = register_read["count"]
            modbusdata = self._client.read_input_registers(address=start_address, count=count, slave=self._hass.data[DOMAIN]["wp_config"]["slave_id"]) 
            if modbusdata.isError():
                _LOGGER.error(f"Error reading registers starting at address {start_address}")
                return False
            else:
                modbusdata_values = {start_address + i: value for i, value in enumerate(modbusdata.registers)}
                modbusdata_input_registers_values.update(modbusdata_values)
                #_LOGGER.debug(f"modbusdata_input_registers_values: {modbusdata_input_registers_values}")
                #_LOGGER.debug(f"modbusdata_values: {modbusdata_values}") 
                self.data.update(modbusdata_values)

        holding_registers = wp_config["holding_registers"]
        modbusdata_holding_registers_values = {}
        for register_read in holding_registers:
            start_address = register_read["start_address"]
            count = register_read["count"]
            try:
                modbusdata = self._client.read_holding_registers(address=start_address, count=count, slave=self._hass.data[DOMAIN]["wp_config"]["slave_id"])
            except Exception as e:
                _LOGGER.error(f"Error reading holding registers starting at address {start_address}: {e}")  
            if modbusdata.isError():
                _LOGGER.error(f"Error reading registers starting at address {start_address}")
                return False
            else:
                modbusdata_values = {start_address + i: value for i, value in enumerate(modbusdata.registers)}
                modbusdata_holding_registers_values.update(modbusdata_values)
                #_LOGGER.debug(f"modbusdata_holding_registers_values: {modbusdata_holding_registers_values}")
                self.data.update(modbusdata_values)

        try:
            # Process data from registers
            added_entities = self._hass.data[DOMAIN][self._name]["added_entities"]
            #_LOGGER.debug(f"Added entities: {added_entities}")
            for wp_register_key, wp_register_object in self._hass.data[DOMAIN]["wp_registers"].items():
                register_number = int(wp_register_object["register_number"])
                #_LOGGER.debug(f"Register number: {register_number}")
                if wp_register_key not in added_entities:
                  continue
                step = float(wp_register_object["step"])
                # Ensure register number exists in modbusdata_values
                register_value = None
                if register_number in modbusdata_input_registers_values:
                    register_value = modbusdata_input_registers_values[register_number]
                elif register_number in modbusdata_holding_registers_values:
                    register_value = modbusdata_holding_registers_values[register_number]
                #if register_number > wp_config["holding_registers_begin"]:
                #_LOGGER.debug(f"Key {wp_register_key} Register {register_number} Registerwert: {register_value}")
                if register_value is not None:
                    if wp_register_object["type"] == "boolean":
                        self.data[wp_register_key] = self.get_boolean_state(register_value, wp_register_key)
                    elif wp_register_object["type"] == "select":
                        my_options = wp_register_object["options"]
                        self.data[wp_register_key] = self.getOperatingMode(register_value,my_options)
                    elif wp_register_object["data_type"] == "INT16":
                        self.data[wp_register_key] = self.checkval(register_value, step)
                    elif wp_register_object["type"] == "energy":
                        self.data[wp_register_key] = self.decode_energy_data(register_value, wp_register_key)
                    else: 
                        self.data[wp_register_key] = self.checkval(register_value, step)
                else:
                    _LOGGER.error(f"Register {register_number} not found for {wp_register_key}")

            return True

        except Exception as e:
            _LOGGER.error(f"Exception in read_modbus_registers: {e}")
            return False

    def get_boolean_state(self, modbusdata_values, key):
        """Helper function to get boolean state from register values."""
        register_value = modbusdata_values.get(key)
        return "off" if register_value == 0 else "on" if register_value else None

    def get_four_way_valve_state(self, modbusdata_values):
        """Helper function to determine four-way valve state."""
        register_value = modbusdata_values.get("fourWayValve")
        return "Abtaubetrieb" if register_value != 0 else "Aus"

    def decode_energy_data(self, modbusdata_values, key, scale=1):
        """Helper function to decode 32-bit unsigned integer energy data."""
        register_value = modbusdata_values.get(key)
        return register_value * scale if register_value else None

    # def read_input_registers(self, address, count, slave):
    #     """Read input registers with error handling."""
    #     with self._lock:
    #         _LOGGER.debug(f"Reading input registers: address={address}, count={count}, slave={slave}")
    #         try:
    #             return self._client.read_input_registers(address=address, count=count, slave=slave)
    #         except Exception as e:
    #             _LOGGER.error(f"Error reading input registers: {e}")
    #             return None  # Oder eine geeignete Fehlerbehandlung

    def getsignednumber(self, number, bitlength=16):
        mask = (2**bitlength) - 1
        if number & (1 << (bitlength - 1)):
            return number | ~mask
        else:
            return number & mask

    def checkval(self, value, scale, bitlength=16):
        """Check value for missing item"""
        if value is None:
            return None
        value = self.getsignednumber(value, bitlength)
        value = round(value * scale, 1)
        if value == -50.0:
            value = None
        return value

    def getOperatingMode(self, operating_mode_nr: int,options):
      """Get the operating mode from the register value."""
      options_hashmap = {
          int(key): value for key, value in options.items()
      }
      #_LOGGER.debug(f"Options: {options_hashmap}")
      return options_hashmap.get(operating_mode_nr, "Not found")  # Use int key lookup


    # def getbetriebsartnr(self, operating_mode_str: str):
    #     config_data = self._hass.data[DOMAIN]["wp_registers"]
    #     options = config_data["operatingMode"]["options"]
    #     for key, value in options.items():
    #         if value == operating_mode_str:
    #             return int(key)
    #     return None

    async def setter_function_callback(self, entity: Entity, option):
        if self._access_mode == "read_only":
            _LOGGER.warning("Write operation attempted in read-only mode.")
            return

        if entity.entity_description.key == "operatingMode":
            await self.set_operatingMode(option)
            return
        if entity.entity_description.key == "mkr1OperatingMode":
            await self.set_mkr1_operatingMode(option)
            return
        if entity.entity_description.key == "mkr2OperatingMode":
            await self.set_mkr2_betriebsart(option)
            return
        if entity.entity_description.key == "desiredRoomTemperature":
            temp = float(option["temperature"])
            await self.set_roomTemperature(temp)
            
        if entity.entity_description.key == "rltMinCooling":
            temp = float(option["temperature"])
            await self.set_rltkuehlen(temp)

        if entity.entity_description.key == "makeHotWater":
            tmin = float(option["target_temp_low"])
            tmax = float(option["target_temp_high"])
            await self.set_ww_bereitung(tmin, tmax)

    async def set_operatingMode(self, operation_mode: str):
      if self._access_mode == "read_only":
            _LOGGER.warning("Write operation attempted in read-only mode.")
            return
      betriebsart_nr = self.getOperatingMode(operation_mode)
      if betriebsart_nr is None:
          return
      config_registers = self._hass.data[DOMAIN]["wp_registers"]
      config = config_registers["operatingMode"]
      self._client.write_register(address=config["register_number"], value=betriebsart_nr, slave=self._hass.data[DOMAIN]["wp_config"]["slave_id"])
      await self.async_refresh_modbus_data()

    async def set_mkr1_operatingMode(self, betriebsart: str):
        if self._access_mode == "read_only":
            _LOGGER.warning("Write operation attempted in read-only mode.")
            return
        betriebsart_nr = self.getOperatingMode(betriebsart)
        if betriebsart_nr is None:
            return
        config_data = self._hass.data[DOMAIN]["wp_registers"]
        config = config_data["mkr1OperatingMode"]
        
        self._client.write_register(address=config["register_number"], value=betriebsart_nr, slave=self._hass.data[DOMAIN]["wp_config"]["slave_id"])
        await self.async_refresh_modbus_data()

    async def set_mkr2_betriebsart(self, betriebsart: str):
      # 112
        if self._access_mode == "read_only":
            _LOGGER.warning("Write operation attempted in read-only mode.")
            return
        betriebsart_nr = self.getOperatingMode(betriebsart)
        if betriebsart_nr is None:
            return
        config_data = self._hass.data[DOMAIN]["wp_registers"]
        config = config_data["mkr2OperatingMode"]
        
        self._client.write_register(address=config["register_number"], value=betriebsart_nr, slave=1)
        await self.async_refresh_modbus_data()

    async def set_roomTemperature(self, temperature: float):
        # 101
        if self._access_mode == "read_only":
            _LOGGER.warning("Write operation attempted in read-only mode.")
            return
        if temperature is None:
            return
        temp_int = int(temperature * 10)
        config_data = self._hass.data[DOMAIN]["wp_registers"]
        config = config_data["desiredRoomTemperature"]
        self._client.write_register(address=config["register_number"], value=temp_int, slave=1)
        await self.async_refresh_modbus_data()

    async def set_rltkuehlen(self, temperature: float):
      # 104
        if self._access_mode == "read_only":
            _LOGGER.warning("Write operation attempted in read-only mode.")
            return
        if temperature is None:
            return
        temp_int = int(temperature * 10)
        config_data = self._hass.data[DOMAIN]["wp_registers"]
        config = config_data["rltMinKuelung"]
        self._client.write_register(address=config["register_number"], value=temp_int, slave=1)
        await self.async_refresh_modbus_data()

    async def set_ww_bereitung(self, temp_min: float, temp_max: float):
        if self._access_mode == "read_only":
            _LOGGER.warning("Write operation attempted in read-only mode.")
            return
        if temp_min is None or temp_max is None:
            return
        temp_max_int = int(temp_max * 10)
        temp_min_int = int(temp_min * 10)
        config_data = self._hass.data[DOMAIN]["wp_registers"]
        config_max = config_data["wwNormaltemp"] # 105
        config_min = config_data["wwMinimaltemp"] # 106
        self._client.write_register(address=config_max["register_number"], value=temp_max_int, slave=1)
        self._client.write_register(address=config_min["register_number"], value=temp_min_int, slave=1)
        await self.async_refresh_modbus_data()
