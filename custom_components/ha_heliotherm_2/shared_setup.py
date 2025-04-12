import logging
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_shared(
    hass, entry, async_add_entities, entity_type_key, entity_class, unit_mapping=None
):
    """Shared setup function for all platforms."""
    hub_name = entry.data["name"]
    hub = hass.data[DOMAIN][hub_name]["hub"]
    entities = hass.data[DOMAIN][entity_type_key]
    wp_config = hass.data[DOMAIN]["wp_config"]
    display_language = entry.data.get("display_language", "en")

    device_info = {
        "identifiers": {(DOMAIN, hub_name)},
        "name": hub_name,
        "manufacturer": wp_config["manufacturer"],
    }
    entity_specific_dict = {}
    #entity_specific_dict["display_language"] = display_language
    entities_to_add = []
    added_entities = set()
    #_LOGGER.debug(f"entities: {entities}")  
    for entity_key, my_entity in entities.items():
        if my_entity.get("omit", False):
            continue
        if my_entity["register_number"] > wp_config["register_number_read_max"]:
            break  # Skip if register number is too high
        if entity_key in added_entities:
            continue  # Skip if already added
        # ❗ Neu initialisieren innerhalb der Schleife
        entity_specific_dict = {}
        # Handle unit mapping if provided
        native_unit_of_measurement = None
        device_class = None
        state_class = None
        if unit_mapping:
            my_unit = my_entity.get("unit")
            my_device_class = my_entity.get("device_class", "default")
            context = my_device_class if my_device_class in unit_mapping.get(my_unit, {}) else "default"
            native_unit_of_measurement, device_class, state_class = unit_mapping.get(my_unit, {}).get(
                context, (None, None, None)
            )
            entity_specific_dict["native_unit_of_measurement"] = native_unit_of_measurement
            entity_specific_dict["device_class"] = device_class
            entity_specific_dict["state_class"] = state_class 
        #_LOGGER.debug(f"Entityclass: {entity_class}")
        # Create the entity
        entity = entity_class(
            hub_name,
            hub,
            device_info,
            my_entity,
            entity_key=entity_key,
            display_language=display_language,
            entity_specific_dict=entity_specific_dict,
        )
        entity._attr_name = entity.name  # Ensure name is set
        _LOGGER.debug(f"Entity: {entity}")
        entities_to_add.append(entity)
        added_entities.add(entity_key)  # Mark as added

    #_LOGGER.debug(f"Entities to add: {[f'{e.__class__.__name__} ({e.entity_id})' for e in entities]}")

    
    hass.data[DOMAIN][hub_name]["added_entities"].update(added_entities)
    _LOGGER.debug(f"Added entities: {added_entities}")
    # Update the hub's added entities
    #hass.data[DOMAIN][hub_name]["added_entities"] = added_entities
    async_add_entities(entities_to_add)