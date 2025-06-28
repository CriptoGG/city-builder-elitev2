import unittest
from city_builder.city import City
from city_builder.buildings import Building
from city_builder.config import INITIAL_CREDITS, INITIAL_POPULATION, INITIAL_POWER, CITY_RANKS, BUILDING_SPECS

class TestCity(unittest.TestCase):

    def setUp(self):
        """Set up a new City instance for each test."""
        self.city = City()

    def test_initial_state(self):
        self.assertEqual(self.city.credits, INITIAL_CREDITS)
        self.assertEqual(self.city.population, INITIAL_POPULATION)
        self.assertEqual(self.city.net_power, INITIAL_POWER) # Initial base power
        self.assertEqual(self.city.total_power_generation, INITIAL_POWER)
        self.assertEqual(self.city.total_power_consumption, 0)
        self.assertEqual(len(self.city.buildings), 0)
        self.assertEqual(self.city.current_rank_level, 0)
        self.assertEqual(self.city.current_rank_name, CITY_RANKS[0]["name"])

    def test_add_building_sufficient_credits(self):
        solar_spec = BUILDING_SPECS["SOLAR_PANEL"]
        success, message = self.city.add_building("SOLAR_PANEL", (0, 0))
        self.assertTrue(success)
        self.assertEqual(len(self.city.buildings), 1)
        self.assertEqual(self.city.credits, INITIAL_CREDITS - solar_spec["cost"])
        self.assertIsNotNone(self.city.grid[0][0])
        self.assertEqual(self.city.grid[0][0].type, "SOLAR_PANEL")

    def test_add_building_insufficient_credits(self):
        self.city.credits = 100 # Not enough for a solar panel (cost 500)
        success, message = self.city.add_building("SOLAR_PANEL", (0, 0))
        self.assertFalse(success)
        self.assertEqual(len(self.city.buildings), 0)
        self.assertEqual(self.city.credits, 100)
        self.assertIn("Not enough credits", message)

    def test_add_building_occupied_space(self):
        self.city.add_building("SOLAR_PANEL", (0, 0))
        success, message = self.city.add_building("SOLAR_PANEL", (0, 0))
        self.assertFalse(success)
        self.assertEqual(len(self.city.buildings), 1) # Only the first one
        self.assertIn("Space already occupied", message)

    def test_add_building_multi_tile(self):
        habitat_spec = BUILDING_SPECS["HABITAT_SMALL"] # size (2,2)
        success, message = self.city.add_building("HABITAT_SMALL", (1,1))
        self.assertTrue(success)
        self.assertEqual(self.city.credits, INITIAL_CREDITS - habitat_spec["cost"])
        self.assertIsNotNone(self.city.grid[1][1])
        self.assertIsNotNone(self.city.grid[2][1])
        self.assertIsNotNone(self.city.grid[1][2])
        self.assertIsNotNone(self.city.grid[2][2])
        self.assertEqual(self.city.grid[1][1].type, "HABITAT_SMALL")

    def test_add_building_out_of_bounds(self):
        from city_builder.config import GRID_WIDTH, GRID_HEIGHT
        success, message = self.city.add_building("SOLAR_PANEL", (GRID_WIDTH, GRID_HEIGHT))
        self.assertFalse(success)
        self.assertIn("Building out of bounds", message)

        # Test multi-tile out of bounds
        success, message = self.city.add_building("HABITAT_SMALL", (GRID_WIDTH - 1, GRID_HEIGHT - 1))
        self.assertFalse(success)
        self.assertIn("Building out of bounds", message)


    def test_remove_building(self):
        solar_spec = BUILDING_SPECS["SOLAR_PANEL"]
        self.city.add_building("SOLAR_PANEL", (0,0))
        self.assertEqual(len(self.city.buildings), 1)

        success, message = self.city.remove_building((0,0))
        self.assertTrue(success)
        self.assertEqual(len(self.city.buildings), 0)
        self.assertIsNone(self.city.grid[0][0])
        self.assertEqual(self.city.credits, INITIAL_CREDITS - solar_spec["cost"] + solar_spec["cost"] // 2)
        self.assertIn("removed", message)

    def test_remove_building_multi_tile(self):
        habitat_spec = BUILDING_SPECS["HABITAT_SMALL"]
        self.city.add_building("HABITAT_SMALL", (1,1)) # size (2,2)

        success, message = self.city.remove_building((1,1)) # Click any part of it
        self.assertTrue(success)
        self.assertEqual(len(self.city.buildings), 0)
        self.assertIsNone(self.city.grid[1][1])
        self.assertIsNone(self.city.grid[2][1])
        self.assertIsNone(self.city.grid[1][2])
        self.assertIsNone(self.city.grid[2][2])
        self.assertEqual(self.city.credits, INITIAL_CREDITS - habitat_spec["cost"] + habitat_spec["cost"] // 2)

    def test_remove_non_existent_building(self):
        success, message = self.city.remove_building((5,5))
        self.assertFalse(success)
        self.assertIn("No building at that position", message)


    def test_update_resources_power(self):
        solar_spec = BUILDING_SPECS["SOLAR_PANEL"]
        habitat_spec = BUILDING_SPECS["HABITAT_SMALL"]

        self.city.add_building("SOLAR_PANEL", (0,0)) # Gen: 50
        self.city.update_resources() # Called internally by add_building

        self.assertEqual(self.city.total_power_generation, INITIAL_POWER + solar_spec["power_gen"])
        self.assertEqual(self.city.total_power_consumption, 0)
        self.assertEqual(self.city.net_power, INITIAL_POWER + solar_spec["power_gen"])

        self.city.add_building("HABITAT_SMALL", (2,2)) # Con: 10
        # update_resources called by add_building
        self.assertEqual(self.city.total_power_generation, INITIAL_POWER + solar_spec["power_gen"])
        self.assertEqual(self.city.total_power_consumption, habitat_spec["power_con"])
        self.assertEqual(self.city.net_power, INITIAL_POWER + solar_spec["power_gen"] - habitat_spec["power_con"])

    def test_update_resources_population_capacity(self):
        habitat_spec = BUILDING_SPECS["HABITAT_SMALL"]
        self.city.add_building("HABITAT_SMALL", (0,0))
        self.assertEqual(self.city.max_population_capacity, habitat_spec["population_cap"])

    def test_population_growth(self):
        self.city.add_building("HABITAT_SMALL", (0,0)) # Capacity 50
        initial_pop = self.city.population

        # Simulate multiple updates for growth
        for _ in range(10): # Should be enough for some growth if logic is 1% of diff
             self.city.update_resources()

        self.assertGreater(self.city.population, initial_pop)
        self.assertLessEqual(self.city.population, self.city.max_population_capacity)

    def test_credits_income(self):
        self.city.add_building("HABITAT_SMALL", (0,0)) # Capacity 50
        # Let population grow a bit
        for _ in range(20):
            self.city.update_resources()

        self.assertGreater(self.city.population, 0)
        initial_credits = self.city.credits
        self.city.update_resources() # One more tick for income
        self.assertEqual(self.city.credits, initial_credits + self.city.population)


    def test_city_value_and_rank_update(self):
        initial_value = self.city.city_value
        self.city.add_building("SOLAR_PANEL", (0,0)) # Value 300
        self.assertGreater(self.city.city_value, initial_value)

        # Test rank up
        self.city.credits = CITY_RANKS[1]["value_needed"] # Artificially boost value by credits
        self.city.update_resources() # This calls update_rank
        self.assertEqual(self.city.current_rank_level, 1)
        self.assertEqual(self.city.current_rank_name, CITY_RANKS[1]["name"])

    def test_ore_production_simulation(self):
        if "ORE_MINE_BASIC" not in BUILDING_SPECS:
            self.skipTest("ORE_MINE_BASIC not in BUILDING_SPECS, skipping ore production simulation test.")

        # Ensure city has enough rank to build ORE_MINE_BASIC if it has a rank requirement
        ore_mine_spec = BUILDING_SPECS["ORE_MINE_BASIC"]
        if ore_mine_spec["unlock_rank"] > self.city.current_rank_level:
            # Artificially increase rank for test if needed - find rank that unlocks it
            for rank_level, rank_info in CITY_RANKS.items():
                if rank_level >= ore_mine_spec["unlock_rank"]:
                    self.city.city_value = rank_info["value_needed"]
                    self.city.update_rank() # update_resources also calls this, but direct call is fine
                    break
            # self.city.current_rank_level = ore_mine_spec["unlock_rank"] # simpler, but less 'real'

        # Add a power source first, as ORE_MINE_BASIC consumes power
        self.city.add_building("SOLAR_PANEL", (0,0)) # 50 power gen + 100 initial = 150 power

        initial_ore = self.city.ore
        success, _ = self.city.add_building("ORE_MINE_BASIC", (2,2)) # Consumes 20, Produces 5 ore
        self.assertTrue(success, "Should be able to add ore mine with sufficient rank and power.")

        self.city.update_resources() # First tick after building, ore might not increase yet depending on exact sequence
                                     # The ore is added during the update_resources based on *existing* operational buildings.
                                     # So, the tick *after* it's built and operational.

        # Let's check if it's operational
        mine_building = next(b for b in self.city.buildings if b.type == "ORE_MINE_BASIC")
        self.assertTrue(mine_building.is_operational, "Mine should be operational with solar panel.")

        self.city.update_resources() # Second tick, ore should have increased

        expected_ore_increase = ore_mine_spec["ore_prod"]
        self.assertEqual(self.city.ore, initial_ore + expected_ore_increase)

        # Test that non-operational mine doesn't produce ore
        # Remove power source
        self.city.remove_building((0,0)) # Remove SOLAR_PANEL
        self.city.update_resources() # Update operational states

        self.assertFalse(mine_building.is_operational, "Mine should be non-operational without power.")

        current_ore_after_power_loss = self.city.ore
        self.city.update_resources() # Another tick
        self.assertEqual(self.city.ore, current_ore_after_power_loss, "Ore should not increase if mine is not operational.")


    def test_power_shortage_operational_status(self):
        # Add one solar panel (100 base + 50 gen = 150 total gen)
        self.city.add_building("SOLAR_PANEL", (0,0))

        # Add habitats that consume more than available power
        # Each Habitat consumes 10. 15 habitats = 150 consumption.
        # 16th should cause issues.
        for i in range(15): # 15 * 10 = 150 consumption. Net power = 0
            self.city.add_building("HABITAT_SMALL", (i // 5 + 1, i % 5 +1)) # Spread them out a bit

        self.city.update_resources()
        self.assertEqual(self.city.net_power, 0) # 150 gen - 150 con
        for building in self.city.buildings:
            if building.type == "HABITAT_SMALL":
                self.assertTrue(building.is_operational)

        # Add one more habitat, pushing consumption over generation
        self.city.add_building("HABITAT_SMALL", (20,20)) # Total consumption 160
        self.city.update_resources()

        self.assertLess(self.city.net_power, 0) # Should be negative if all were on

        # Check that at least one habitat was turned off
        operational_habitats = sum(1 for b in self.city.buildings if b.type == "HABITAT_SMALL" and b.is_operational)
        total_habitats = sum(1 for b in self.city.buildings if b.type == "HABITAT_SMALL")

        self.assertLess(operational_habitats, total_habitats)
        # The number of operational buildings should result in non-negative net power,
        # or all consumers are off and it's still negative (if base power also negative, not the case here)

        # Recalculate power based on operational buildings
        final_gen = INITIAL_POWER + BUILDING_SPECS["SOLAR_PANEL"]["power_gen"]
        final_con = sum(b.power_consumption for b in self.city.buildings if b.is_operational and b.type == "HABITAT_SMALL")
        self.assertEqual(self.city.net_power, final_gen - final_con)
        self.assertGreaterEqual(self.city.net_power, 0) # Power system should balance by shutting down

        # Check population capacity is reduced due to non-operational habitat
        expected_max_pop = operational_habitats * BUILDING_SPECS["HABITAT_SMALL"]["population_cap"]
        self.assertEqual(self.city.max_population_capacity, expected_max_pop)


if __name__ == '__main__':
    unittest.main()
