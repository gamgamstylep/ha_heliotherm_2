import unittest
from unittest.mock import MagicMock
from custom_components.ha_heliotherm_2.ha_heliotherm_select import HeliothermSelect

class TestHeliothermSelect(unittest.TestCase):
  def setUp(self):
    self.platform_name = "test_platform"
    self.hub = MagicMock()
    self.device_info = {"identifiers": {("domain", "unique_id")}}
    self.register = "test_register"
    self.register_key = "test_key"
    self.options = ["option1", "option2", "option3"]
    self.default_value = "option1"
    self.display_language = "en"

  def test_init(self):
    select_entity = HeliothermSelect(
      self.platform_name,
      self.hub,
      self.device_info,
      self.register,
      self.register_key,
      self.options,
      self.default_value,
      self.display_language
    )

    self.assertEqual(select_entity._attr_options, self.options)
    self.assertEqual(select_entity._attr_current_option, self.default_value)
    self.assertEqual(select_entity.entity_description.key, self.register_key)
    self.assertEqual(select_entity.entity_description.name, select_entity.name)

if __name__ == "__main__":
  unittest.main()