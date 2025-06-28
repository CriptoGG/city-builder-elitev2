import unittest
import os
import json
from city_builder.city import City
from city_builder.save_load import save_game, load_game, SAVE_GAME_DIR
from city_builder.config import INITIAL_CREDITS

class TestSaveLoad(unittest.TestCase):

    def setUp(self):
        self.test_city = City()
        self.test_save_filename = "unittest_save.json"
        self.test_save_filepath = os.path.join(SAVE_GAME_DIR, self.test_save_filename)

        # Ensure save directory exists for tests
        if not os.path.exists(SAVE_GAME_DIR):
            os.makedirs(SAVE_GAME_DIR)

        # Clean up any old test save file before each test
        if os.path.exists(self.test_save_filepath):
            os.remove(self.test_save_filepath)

    def tearDown(self):
        # Clean up test save file after each test
        if os.path.exists(self.test_save_filepath):
            os.remove(self.test_save_filepath)
        # Clean up directory if empty, careful not to delete user saves
        if os.path.exists(SAVE_GAME_DIR) and not os.listdir(SAVE_GAME_DIR) and "unittest" in self.test_save_filename:
            try:
                os.rmdir(SAVE_GAME_DIR)
            except OSError: # Might fail if other files are present, which is fine.
                pass


    def test_save_game_creates_file(self):
        self.test_city.add_building("SOLAR_PANEL", (0,0))
        self.test_city.credits = 5000

        save_successful = save_game(self.test_city, self.test_save_filename)
        self.assertTrue(save_successful)
        self.assertTrue(os.path.exists(self.test_save_filepath))

        # Verify content (basic check)
        with open(self.test_save_filepath, 'r') as f:
            data = json.load(f)
        self.assertEqual(data["credits"], 5000)
        self.assertEqual(len(data["buildings"]), 1)
        self.assertEqual(data["buildings"][0]["type"], "SOLAR_PANEL")

    def test_load_game_restores_city(self):
        # First, create a city and save it
        original_city = City()
        original_city.add_building("SOLAR_PANEL", (1,1))
        original_city.add_building("HABITAT_SMALL", (3,3))
        original_city.credits = 12345
        original_city.population = 67
        original_city.ore = 890
        original_city.city_value = 50000 # Will trigger rank update
        original_city.update_resources() # To get rank and other derived values correct

        save_game(original_city, self.test_save_filename)

        # Now load it
        loaded_city = load_game(self.test_save_filename)
        self.assertIsNotNone(loaded_city)

        self.assertEqual(loaded_city.credits, original_city.credits)
        self.assertEqual(loaded_city.population, original_city.population) # Population is based on capacity after load now
        self.assertEqual(loaded_city.ore, original_city.ore)
        self.assertEqual(len(loaded_city.buildings), len(original_city.buildings))
        self.assertEqual(loaded_city.current_rank_level, original_city.current_rank_level)

        # Check building details (position and type for one of them)
        # Note: Building order might not be guaranteed by dicts/json, so find them
        loaded_solar = next((b for b in loaded_city.buildings if b.type == "SOLAR_PANEL"), None)
        original_solar = next((b for b in original_city.buildings if b.type == "SOLAR_PANEL"), None)
        self.assertIsNotNone(loaded_solar)
        self.assertEqual(loaded_solar.position, original_solar.position)

        loaded_habitat = next((b for b in loaded_city.buildings if b.type == "HABITAT_SMALL"), None)
        original_habitat = next((b for b in original_city.buildings if b.type == "HABITAT_SMALL"), None)
        self.assertIsNotNone(loaded_habitat)
        self.assertEqual(loaded_habitat.position, original_habitat.position)
        self.assertTrue(loaded_habitat.is_operational) # Assuming enough power from solar

        # Test derived values are recalculated correctly
        # (max_population_capacity, net_power, etc. are handled by City.from_dict via update_resources)
        self.assertGreater(loaded_city.max_population_capacity, 0)
        self.assertNotEqual(loaded_city.net_power, 0) # Should be positive with a solar panel and habitat

    def test_load_game_non_existent_file(self):
        loaded_city = load_game("non_existent_save.json")
        self.assertIsNone(loaded_city)

    def test_load_game_corrupted_json(self):
        # Create a corrupted JSON file
        if not os.path.exists(SAVE_GAME_DIR): # ensure_save_dir_exists is not part of save_load module
            os.makedirs(SAVE_GAME_DIR)
        with open(self.test_save_filepath, 'w') as f:
            f.write("this is not json {")

        loaded_city = load_game(self.test_save_filename)
        self.assertIsNone(loaded_city) # Should handle decode error gracefully

    def test_save_and_load_empty_city(self):
        empty_city = City()
        save_successful = save_game(empty_city, self.test_save_filename)
        self.assertTrue(save_successful)

        loaded_city = load_game(self.test_save_filename)
        self.assertIsNotNone(loaded_city)
        self.assertEqual(len(loaded_city.buildings), 0)
        self.assertEqual(loaded_city.credits, INITIAL_CREDITS)


if __name__ == '__main__':
    unittest.main()
