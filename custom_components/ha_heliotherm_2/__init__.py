"""The HaHeliotherm_2 integration."""
# Issues:
# 1. Config read only or read/write cannot be changed after initial setup
# setter_function_callback should work automatically for all entities
from __future__ import annotations
try:
  import asyncio
  from datetime import timedelta
  import logging
  _LOGGER = logging.getLogger(__name__)
  _LOGGER.debug("Lade ha_heliotherm_2...")
  import threading
  from homeassistant.core import callback
  from typing import Optional
  import json
  import aiofiles
  import inspect
  import os
  import logging

  # Get the logger for your custom component (use your component's name)

  from pymodbus.client import ModbusTcpClient
  #from pymodbus.constants import Endian
  from pymodbus.exceptions import ConnectionException
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
  from homeassistant.helpers.event import async_track_time_interval

  # Bestimme den Pfad zur JSON-Datei relativ zur __init__.py
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  JSON_PATH = os.path.join(BASE_DIR, "heliotherm_config.json")


  from .const import DOMAIN


  config_file_path = JSON_PATH

  # Store the loaded config data (None initially)
  wp_json_config_data = None
except Exception as e:
    _LOGGER.exception("Fehler beim Initialisieren: %s", e)

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

async def get_combined_entity(hass, combined_entity):
  """Get the combined entity for a given entity."""
  entities = hass.data[DOMAIN]["entities"]
  _LOGGER.debug(f"Combined entity vor: {combined_entity}")
  combined_entity_original = combined_entity.copy()
  is_first = True
  for attribute_key, attribute_value in combined_entity_original.get("attributes_from_register").items():
    if "register_numbers" not in combined_entity:
            combined_entity["register_numbers"] = {}
    _LOGGER.debug(f"attribute_key: {attribute_key}")
    combined_entity["register_numbers"][attribute_key] = entities.get(attribute_value, {}).get("register_number")
    if is_first:
      excluded_keys = {"description", "supported_features", "type"}
      for entity_key, entity_value in entities.get(attribute_value, {}).items():
          #_LOGGER.debug(f"combined Entity_key: {entity_key}, Entity_value: {entity_value}")
          if entity_key not in excluded_keys:
              combined_entity[entity_key] = entity_value
      is_first = False
  return combined_entity

async def async_setup(hass, config):
  try:
    """Set up the HaHeliotherm modbus component."""
    # reset hass.data[DOMAIN]
    hass.data[DOMAIN] = {}
    """Set up the custom component."""
    # Load configuration asynchronously (only once)
    wp_json_config_data = await load_config_once()
    if wp_json_config_data["config"]["logging"]["level"] == "DEBUG":
      _LOGGER.setLevel(logging.DEBUG)
    else:
      _LOGGER.setLevel(logging.INFO)
    access_mode = hass.data[DOMAIN]["wp_config_access_mode"] if "wp_config_access_mode" in hass.data[DOMAIN] else "read_only"

    # Store the configuration data in hass.data for other components or entities to access
    
    filtered_entities = {k: v for k, v in wp_json_config_data["entities"].items() if not v.get("omit", False)}
    additional_entities = {k: v for k, v in wp_json_config_data["additional_entities"].items() if not v.get("omit", False)}
    additional_sensor_entities = {k: v for k, v in additional_entities.items() if v["type"] == "sensor"}
    
    hass.data[DOMAIN]["wp_config"] = wp_json_config_data["config"]

    hass.data[DOMAIN]["entities"] = filtered_entities
    hass.data[DOMAIN]["combined_entities"] = wp_json_config_data.get("combined_entities", {})
    entities_combined = {k: v for k, v in wp_json_config_data["combined_entities"].items() if not v.get("omit", False)}
    _LOGGER.debug(f"Entities combined: {entities_combined}")
    entities_combinded_enriched = {}
    for entity_key, entity_value in entities_combined.items():
        if entity_value.get("omit", False):
            continue
        if entity_value.get("combined_entity", False):
            combined_entity = await get_combined_entity(hass, entity_value)
            if combined_entity:
                #_LOGGER.debug(f"Combined entity: {combined_entity}")
                # Add the combined entity to the enriched dictionary
                entities_combinded_enriched[entity_key] = combined_entity
                #_LOGGER.debug(f"my_entity updated with combined: {entity_value}")
        else:
            # Add the original entity to the enriched dictionary
            entities_combinded_enriched[entity_key] = entity_value
    #_LOGGER.debug(f"Entities combined enriched: {entities_combinded_enriched}")
    # Add the enriched combined entities to hass.data[DOMAIN]["entities"]
    filtered_entities.update(entities_combinded_enriched)
    hass.data[DOMAIN]["entities"] = filtered_entities
    #_LOGGER.debug(f"hass_entities: {hass.data[DOMAIN]["entities"]}")
    hass.data[DOMAIN]["additional_entities"] = additional_entities
    sensor_entities = {k: v for k, v in filtered_entities.items() if v["type"] == "sensor"}
    binary_sensor_entities = {k: v for k, v in filtered_entities.items() if v["type"] == "binary"}  
    entities_climate = {k: v for k, v in filtered_entities.items() if v["type"] == "climate"}
    select_entities = {k: v for k, v in filtered_entities.items() if v["type"] == "select"}
    #entities_climate_combined = {k: v for k, v in entities_combined.items() if v["type"] == "climate"}
    hass.data[DOMAIN]["entities_sensor"] = sensor_entities
    hass.data[DOMAIN]["entities_binary_sensor"] = binary_sensor_entities
    hass.data[DOMAIN]["entities_climate"] = entities_climate
    #hass.data[DOMAIN]["entities_climate_combined"] = entities_climate_combined
    hass.data[DOMAIN]["entities_select"] = select_entities
    return True
  except Exception as e:
    _LOGGER.exception("Fehler beim async_setup: %s", e)

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

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
  try:
    """Set up a HaHeliotherm modbus."""
    # from initial setup GUI - config flow
    host = entry.data[CONF_HOST] # from config flow
    name = entry.data[CONF_NAME] # from config flow
    port = entry.data[CONF_PORT] # from config flow
    display_language = entry.data.get("display_language", "en") # from config flow
    access_mode = entry.data.get("access_mode", "read_only") # from config flow
    hass.data[DOMAIN]["wp_config_access_mode"] = access_mode
    
    wp_config = hass.data[DOMAIN]["wp_config"]
    
    scan_interval =  wp_config.get("default_scan_interval")

    _LOGGER.debug("Setup %s.%s", DOMAIN, name)

    hub = HaHeliothermModbusHub(hass, name, host, port, scan_interval, access_mode, display_language)
    # """Register the hub."""
    hass.data[DOMAIN][name] = {"hub": hub}
    hass.data[DOMAIN][name]["added_entities"] = set()
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor", "climate", "select"])
    return True
  except Exception as e:
    _LOGGER.exception("Fehler beim async_setup_entry: %s", e)

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
            
    async def write_register_with_protection(self, address, value, modbus_unit_id, entity_id):
        config = self._hass.data[DOMAIN]["entities"][entity_id]
        write_protected = True
        function_name = inspect.currentframe().f_code.co_name
        if "write_protected" in config:
          write_protected = config["write_protected"]
          _LOGGER.debug(f"{function_name}:Write protect: {write_protected} for {entity_id} with address {address} and value {value}")
        if write_protected:
          _LOGGER.debug(f"{function_name}:Write protection is enabled. Cannot perform write operation for {entity_id} with address {address} and value {value}")
          return False
        # If no protection, proceed with the write operation
        if type(value) != int:
            _LOGGER.error(f"{function_name}:Invalid value {value} (datentyp:{type(value)}) (type: {value.__name__}) for {entity_id} with address {address}")
            return False
        try:
            self._client.write_register(address=address, value=value)
            #_LOGGER.debug(f"{function_name}:Successfully wrote value {value} to address {address} on unit {unit}")
            return True
        except Exception as e:
            #_LOGGER.debug(f"{function_name}:Failed to write register: {e}")
            return False
            
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
            modbusdata = self._client.read_input_registers(address=start_address, count=count) 
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
                modbusdata = self._client.read_holding_registers(address=start_address, count=count)
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
            for entity_key in added_entities:
                # self._hass.data[DOMAIN]["entities"].items():
                wp_entity_object = self._hass.data[DOMAIN]["entities"].get(entity_key)
                if wp_entity_object is None:
                    wp_entity_object = self._hass.data[DOMAIN]["combined_entities"].get(entity_key)
                if wp_entity_object is None:
                    _LOGGER.error(f"Entity {entity_key} not found in config")
                    continue
                #_LOGGER.debug(f"Entity key: {entity_key} wp_entity_object: {wp_entity_object}")
                #if wp_entity_object.get("combined_entity", False):
                register_number = int(wp_entity_object["register_number"])
                #_LOGGER.debug(f"Register number: {register_number}")
                step = float(wp_entity_object["step"])
                # Ensure register number exists in modbusdata_values
                register_value = None
                if register_number in modbusdata_input_registers_values:
                    register_value = modbusdata_input_registers_values[register_number]
                elif register_number in modbusdata_holding_registers_values:
                    register_value = modbusdata_holding_registers_values[register_number]
                #if register_number > wp_config["holding_registers_begin"]:
                #_LOGGER.debug(f"Key {entity_key} Register {register_number} Registerwert: {register_value}")
                multiplier = wp_entity_object.get("multiplier", 1)
                if register_value is not None:
                    if wp_entity_object["type"] == "boolean":
                        self.data[entity_key] = self.get_boolean_state(register_value, entity_key)
                    elif wp_entity_object["type"] == "select":
                        my_options = wp_entity_object["options"]
                        self.data[entity_key] = self.get_operating_mode_string(register_value,my_options)
                    elif wp_entity_object["type"] == "climate":
                        _LOGGER.debug(f"Climate register: {entity_key} with value {register_value}")
                        self.data[entity_key] = self.checkval(register_value, multiplier)
                    elif wp_entity_object["data_type"] == "INT16":
                        self.data[entity_key] = self.checkval(register_value, multiplier)
                    elif wp_entity_object["type"] == "energy":
                        self.data[entity_key] = self.decode_energy_data(register_value, entity_key)
                    else: 
                        self.data[entity_key] = self.checkval(register_value, multiplier)
                else:
                    _LOGGER.error(f"Register {register_number} not found for {entity_key}")

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

    def getsignednumber(self, number, bitlength=16):
        mask = (2**bitlength) - 1
        if number & (1 << (bitlength - 1)):
            return number | ~mask
        else:
            return number & mask

    def checkval(self, value, multiplier, bitlength=16):
        """Check value for missing item"""
        if value is None:
            return None
        value = self.getsignednumber(value, bitlength)
        value = round(value * multiplier, 1)
        if value == -50.0:
            value = None
        return value

    def get_operating_mode_string(self, operating_mode_nr: int,options):
      """Get the operating mode from the register value."""
      options_hashmap = {
          int(key): value for key, value in options.items()
      }
      #_LOGGER.debug(f"Options: {options_hashmap}")
      return options_hashmap.get(operating_mode_nr, "Not found")  # Use int key lookup

    def get_operating_mode_number(self, operating_mode_name: str, options: dict):
      #_LOGGER.debug(f"Received options in get_operating_mode_number: {options} (type: {type(options).__name__})")
      options_reversed = {v: k for k, v in options.items()}
      #_LOGGER.debug(f"Options: {options_reversed}")
      return options_reversed.get(operating_mode_name)  # Lookup by string key

    async def setter_function_callback(self, entityObject: Entity, option, custom_data):
        _LOGGER.debug(f"custom_data {custom_data}")
        _LOGGER.debug(f"entityObject {entityObject}")
        entity = custom_data.get("entity", None)  
        entity_type = entity.get("type", None) if entity else None
        entity_key = custom_data.get("entity_key") if custom_data else None
        combined_entity = entity.get("combined_entity", False)
        # auf climate und combined_entities umstellen statt nur für hotwater_min_max
        # if entityObject.entity_description.key == "hotwater_min_max":
        _LOGGER.debug(f"entity_type {entity_type} and entity_key {entity_key} and combined_entity {combined_entity}")
        if entity_type == "climate" and combined_entity:
            _LOGGER.debug(f"Setting hot water min/max to {option}")
            target_temperature_low_entity_key = entityObject._entity.get("attributes_from_register").get("target_temperature_low")
            #_LOGGER.debug(f"target_temperature_low_entity_key: {target_temperature_low_entity_key}")
            _LOGGER.debug(f"hotwater: Setter function callback for {entityObject.entity_description.key} with option {option}")
            target_temperature_high_entity_key = entityObject._entity.get("attributes_from_register").get("target_temperature_high")
            _LOGGER.debug(f"target_temperature_high_entity_key: {target_temperature_high_entity_key}")
            # warum target_temp_high und target_temp_low und nicht target_temperature_low und target_temperature_high?
            temperature = float(option["target_temp_low"])
            _LOGGER.debug(f"target_temp_low: {temperature}")
            await self.set_temperature(temperature, target_temperature_low_entity_key)
            temperature = float(option["target_temp_high"])
            await self.set_temperature(temperature, target_temperature_high_entity_key)
        if entity_type == "select":
            _LOGGER.debug(f"Setting select from entity_type option for {entity_type}:{entityObject.entity_description.key} to {option}")
            await self.set_operating_mode(option, entity_key)
            return
        if entity_type == "climate" and not combined_entity:
            _LOGGER.debug(f"Setting climate from entity_type option for {entity_type}:{entityObject.entity_description.key} to {option}")
            if isinstance(option, dict) and "temperature" in option:
                temperature = option["temperature"]
            else:
                temperature = option  # fallback, in case option is already a float/int
            await self.set_temperature(temperature, entity_key)
            return

    async def set_operating_mode(self, operation_mode: str, register_id):
      #_LOGGER.debug(f"Trying to set {operation_mode} for {register_id}")
      #register_id = "operating_mode"
      config_data = self._hass.data[DOMAIN]["entities"]
      config = config_data[register_id]
      config_options = config["options"]
      #_LOGGER.debug(f"Options: {type(config_options)}:{config_options}")
      #_LOGGER.debug(f"config['options']: {config['options']} (type: {type(config['options']).__name__})")
      #_LOGGER.debug(f"get_operating_mode_number called with: {operation_mode}, {config['options']} (type: {type(config['options']).__name__})")
      operation_mode_nr = int(self.get_operating_mode_number(operating_mode_name=operation_mode,options=config_options))
      #_LOGGER.debug(f"Received options in get_operating_mode_number: {operation_mode_nr} (type: {type(operation_mode_nr).__name__})")
      if not isinstance(operation_mode_nr, int):
        #_LOGGER.error(f"Invalid operating mode '{operation_mode_nr}' for {register_id}")
        return
      #_LOGGER.debug(f"Setting for {register_id} to {operation_mode} with value {operation_mode_nr}")
      function_name = inspect.currentframe().f_code.co_name
      myAddress = config["register_number"]
      myValue = operation_mode_nr
      modbus_unit_id = self._hass.data[DOMAIN]["wp_config"]["config"].get("modbus_unit_id", 1)
      #_LOGGER.debug(f"Setting for {function_name} to {operation_mode} with value {myValue}")
      if self._access_mode == "read_only":
            _LOGGER.warning(f"Write operation attempted in read-only mode for {function_name} to {operation_mode} with value {myValue}.")
            #return
      await self.write_register_with_protection(address=myAddress, value=myValue, modbus_unit_id=modbus_unit_id, entity_id=register_id)
      await self.async_refresh_modbus_data()

    async def set_temperature(self, temperature: float, entity_id):
        # 101
        my_function_name = inspect.currentframe().f_code.co_name
        if temperature is None:
            _LOGGER.error(f"{my_function_name:} No temperature provided to set for {entity_id}")
            return
        _LOGGER.debug(f"Trying to set {temperature} for {entity_id}")
        
        config_data = self._hass.data[DOMAIN]["entities"]
        config = config_data[entity_id]
        myAddress = config["register_number"]
        _LOGGER.debug(f"temperature_what_is_IT: {temperature}")
        myValue = int(temperature / config.get("multiplier", 1))
        modbus_unit_id = self._hass.data[DOMAIN]["wp_config"]["config"].get("modbus_unit_id", 1)
        if self._access_mode == "read_only":
            _LOGGER.warning(f"Write operation attempted in read-only mode for {my_function_name} to {entity_id} to myAddress {myAddress} with value {myValue}.")
            return
        await self.write_register_with_protection(address=myAddress, value=myValue, modbus_unit_id=modbus_unit_id, entity_id=entity_id)
        await self.async_refresh_modbus_data()