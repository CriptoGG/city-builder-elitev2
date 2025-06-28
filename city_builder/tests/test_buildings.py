import unittest
from city_builder.buildings import Building, get_available_buildings
from city_builder.config import BUILDING_SPECS

class TestBuilding(unittest.TestCase):

    def test_create_building(self):
        solar_spec = BUILDING_SPECS["SOLAR_PANEL"]
        building = Building("SOLAR_PANEL", (1, 2))
        self.assertEqual(building.type, "SOLAR_PANEL")
        self.assertEqual(building.name, solar_spec["name"])
        self.assertEqual(building.position, (1, 2))
        self.assertEqual(building.cost, solar_spec["cost"])
        self.assertEqual(building.power_generation, solar_spec["power_gen"])
        self.assertEqual(building.power_consumption, solar_spec["power_con"])
        self.assertEqual(building.size, solar_spec["size"])
        self.assertEqual(building.char, solar_spec["char"])
        self.assertEqual(building.value, solar_spec["value"])
        self.assertTrue(building.is_operational)

    def test_create_building_invalid_type(self):
        with self.assertRaises(ValueError):
            Building("NON_EXISTENT_TYPE", (0, 0))

    def test_get_net_power(self):
        building = Building("SOLAR_PANEL", (0,0)) # Gen 50, Con 0
        self.assertEqual(building.get_net_power(), 50)

        building_consumer = Building("HABITAT_SMALL", (1,1)) # Gen 0, Con 10
        self.assertEqual(building_consumer.get_net_power(), -10)

        building_consumer.is_operational = False
        self.assertEqual(building_consumer.get_net_power(), 0)


    def test_get_population_capacity(self):
        building = Building("HABITAT_SMALL", (0,0)) # Cap 50
        self.assertEqual(building.get_population_capacity(), BUILDING_SPECS["HABITAT_SMALL"]["population_cap"])

        building.is_operational = False
        self.assertEqual(building.get_population_capacity(), 0)

        building_no_pop_cap = Building("SOLAR_PANEL", (0,0))
        self.assertEqual(building_no_pop_cap.get_population_capacity(), 0)

    def test_get_ore_production(self):
        # Assuming ORE_MINE_BASIC is configured in BUILDING_SPECS for testing
        # It might be better to mock BUILDING_SPECS or add a test-specific spec
        # For now, we rely on the existing config.
        if "ORE_MINE_BASIC" not in BUILDING_SPECS:
            self.skipTest("ORE_MINE_BASIC not in BUILDING_SPECS, skipping ore production test.")

        building = Building("ORE_MINE_BASIC", (0,0))
        self.assertEqual(building.get_ore_production(), BUILDING_SPECS["ORE_MINE_BASIC"]["ore_prod"])

        building.is_operational = False
        self.assertEqual(building.get_ore_production(), 0)

        building_no_ore_prod = Building("SOLAR_PANEL", (0,0)) # Solar panels don't produce ore
        self.assertEqual(building_no_ore_prod.get_ore_production(), 0)


    def test_building_to_dict(self):
        building = Building("SOLAR_PANEL", (3, 4))
        building.is_operational = False # Test non-default state
        data = building.to_dict()
        expected_data = {
            "type": "SOLAR_PANEL",
            "position_x": 3,
            "position_y": 4,
            "is_operational": False
        }
        self.assertEqual(data, expected_data)

    def test_building_from_dict(self):
        data = {
            "type": "HABITAT_SMALL",
            "position_x": 5,
            "position_y": 6,
            "is_operational": True
        }
        building = Building.from_dict(data)
        habitat_spec = BUILDING_SPECS["HABITAT_SMALL"]
        self.assertEqual(building.type, "HABITAT_SMALL")
        self.assertEqual(building.name, habitat_spec["name"])
        self.assertEqual(building.position, (5, 6))
        self.assertEqual(building.cost, habitat_spec["cost"])
        self.assertTrue(building.is_operational)

    def test_building_from_dict_default_operational(self):
        # Test loading older save data that might not have 'is_operational'
        data = {
            "type": "SOLAR_PANEL",
            "position_x": 1,
            "position_y": 1
            # "is_operational" is missing
        }
        building = Building.from_dict(data)
        self.assertTrue(building.is_operational) # Should default to True

    def test_get_available_buildings(self):
        # Assuming SOLAR_PANEL and HABITAT_SMALL are rank 0
        # Add a new building for rank 1 for testing
        original_building_specs = BUILDING_SPECS.copy() # Keep a copy
        BUILDING_SPECS["ADV_SOLAR"] = {
            "name": "Advanced Solar", "cost": 2000, "power_gen": 200, "size": (1,1),
            "char": "A", "unlock_rank": 1, "value": 1500
        }

        available_rank_0 = get_available_buildings(0)
        self.assertIn("SOLAR_PANEL", available_rank_0)
        self.assertIn("HABITAT_SMALL", available_rank_0)
        self.assertNotIn("ADV_SOLAR", available_rank_0)

        available_rank_1 = get_available_buildings(1)
        self.assertIn("SOLAR_PANEL", available_rank_1)
        self.assertIn("HABITAT_SMALL", available_rank_1)
        self.assertIn("ADV_SOLAR", available_rank_1)
        self.assertEqual(available_rank_1["ADV_SOLAR"]["name"], "Advanced Solar")

        # Restore original BUILDING_SPECS to not affect other tests if run in same suite
        BUILDING_SPECS.clear()
        BUILDING_SPECS.update(original_building_specs)


if __name__ == '__main__':
    unittest.main()
