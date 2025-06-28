# Elite 1984 City Builder - City Logic

from typing import List, Tuple, Dict, Any
from city_builder.buildings import Building
from city_builder.config import (
    INITIAL_CREDITS, INITIAL_POWER, INITIAL_POPULATION, INITIAL_ORE,
    CITY_RANKS, GRID_WIDTH, GRID_HEIGHT
)

class City:
    """
    Manages the state of the player's city, including resources, buildings, and rank.
    """
    def __init__(self):
        self.buildings: List[Building] = []
        self.credits: int = INITIAL_CREDITS
        self.population: int = INITIAL_POPULATION
        self.ore: int = INITIAL_ORE
        # Power related
        self.total_power_generation: int = 0
        self.total_power_consumption: int = 0
        self.net_power: int = INITIAL_POWER # Net power available to the city

        self.max_population_capacity: int = 0
        self.city_value: int = 0
        self.current_rank_level: int = 0
        self.current_rank_name: str = CITY_RANKS[0]["name"]

        # Grid to keep track of occupied cells for faster collision detection
        self.grid: List[List[Building | None]] = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

        self.update_resources() # Initial calculation

    def add_building(self, building_type: str, position: Tuple[int, int]) -> Tuple[bool, str]:
        """
        Adds a building to the city if affordable and space is available.
        Returns (success, message).
        """
        try:
            temp_building = Building(building_type, position)
        except ValueError as e:
            return False, str(e)

        if self.credits < temp_building.cost:
            return False, "Not enough credits."

        # Check grid boundaries and collision
        pos_x, pos_y = position
        size_w, size_h = temp_building.size
        if not (0 <= pos_x < GRID_WIDTH and 0 <= pos_y < GRID_HEIGHT and
                0 <= pos_x + size_w -1 < GRID_WIDTH and 0 <= pos_y + size_h -1 < GRID_HEIGHT):
            return False, "Building out of bounds."

        for x_offset in range(size_w):
            for y_offset in range(size_h):
                if self.grid[pos_x + x_offset][pos_y + y_offset] is not None:
                    return False, "Space already occupied."

        # Place building
        self.credits -= temp_building.cost
        self.buildings.append(temp_building)
        for x_offset in range(size_w):
            for y_offset in range(size_h):
                self.grid[pos_x + x_offset][pos_y + y_offset] = temp_building

        self.update_resources()
        return True, f"{temp_building.name} placed."

    def remove_building(self, position: Tuple[int, int]) -> Tuple[bool, str]:
        """
        Removes a building from the city at the given grid position.
        Refunds a portion of the cost.
        """
        building_to_remove = None
        for b in self.buildings:
            # Check if the given position is within the building's footprint
            bx, by = b.position
            bw, bh = b.size
            if bx <= position[0] < bx + bw and by <= position[1] < by + bh:
                building_to_remove = b
                break

        if not building_to_remove:
            return False, "No building at that position."

        # Clear from grid
        bx, by = building_to_remove.position
        bw, bh = building_to_remove.size
        for x_offset in range(bw):
            for y_offset in range(bh):
                if 0 <= bx + x_offset < GRID_WIDTH and 0 <= by + y_offset < GRID_HEIGHT:
                    self.grid[bx + x_offset][by + y_offset] = None

        self.buildings.remove(building_to_remove)
        self.credits += building_to_remove.cost // 2 # Refund 50%
        self.update_resources()
        return True, f"{building_to_remove.name} removed. {building_to_remove.cost // 2} credits refunded."


    def update_resources(self) -> None:
        """
        Recalculates all resource totals, power status, population capacity, and city value.
        This should be called after any change to buildings or periodically.
        """
        self.total_power_generation = INITIAL_POWER # Base power
        self.total_power_consumption = 0
        self.max_population_capacity = 0
        current_city_value = 0

        # First pass: determine operational status based on power
        # Assume all buildings are operational initially for calculation
        for building in self.buildings:
            building.is_operational = True # Reset for recalculation
            self.total_power_generation += building.power_generation
            self.total_power_consumption += building.power_consumption

        self.net_power = self.total_power_generation - self.total_power_consumption

        if self.net_power < 0:
            # Power shortage: start turning off non-essential buildings
            # This is a simple approach: turn off consumers one by one until power is balanced or all are off.
            # A more sophisticated approach might prioritize certain buildings.
            sorted_consumers = sorted([b for b in self.buildings if b.power_consumption > 0 and b.power_generation == 0],
                                      key=lambda b: b.power_consumption, reverse=True) # Heaviest consumers first

            temp_net_power = self.net_power
            for building in sorted_consumers:
                if temp_net_power < 0:
                    building.is_operational = False
                    # Recalculate consumption without this building
                    temp_net_power += building.power_consumption # Add back its consumption
                else:
                    break

            # Recalculate actual totals with non-operational buildings
            self.total_power_generation = INITIAL_POWER
            self.total_power_consumption = 0
            for building in self.buildings:
                if building.is_operational:
                    self.total_power_generation += building.power_generation
                    self.total_power_consumption += building.power_consumption
                # else: power gen/con is 0 if not operational
            self.net_power = self.total_power_generation - self.total_power_consumption


        # Second pass: calculate capacities and value based on operational status
        for building in self.buildings:
            current_city_value += building.value
            if building.is_operational:
                self.max_population_capacity += building.get_population_capacity()
                # Add ore production here if implemented
                self.ore += building.get_ore_production() # If per-tick
            # else: non-operational buildings don't contribute these

        # Population growth (simple model for now)
        if self.net_power >= 0: # Only grow if there's power
            if self.population < self.max_population_capacity:
                growth = (self.max_population_capacity - self.population) * 0.01 # Grow by 1% of remaining capacity
                self.population += max(0, int(growth)) # Ensure at least 0 growth, and integer population
            elif self.population > self.max_population_capacity:
                self.population = self.max_population_capacity # Cap population

        # Credits income (simple model: 1 credit per person per update cycle)
        if self.net_power >= 0:
            self.credits += self.population

        self.city_value = current_city_value + self.credits + (self.population * 10) + (self.ore * 2) # Example valuation

        self.update_rank()

    def update_rank(self) -> None:
        """Updates the city's rank based on its value."""
        new_rank_level = self.current_rank_level
        for rank_level, rank_info in CITY_RANKS.items():
            if self.city_value >= rank_info["value_needed"]:
                if rank_level > new_rank_level:
                    new_rank_level = rank_level
            else:
                # Ranks are ordered, so if we don't meet this one, we won't meet higher ones
                break

        if new_rank_level != self.current_rank_level:
            self.current_rank_level = new_rank_level
            self.current_rank_name = CITY_RANKS[self.current_rank_level]["name"]
            # Potentially trigger an event or message about ranking up

    def to_dict(self) -> Dict[str, Any]:
        """Serializes city data to a dictionary for saving."""
        return {
            "buildings": [b.to_dict() for b in self.buildings],
            "credits": self.credits,
            "population": self.population,
            "ore": self.ore,
            "current_rank_level": self.current_rank_level,
            # Net power, capacities, etc., are recalculated on load based on buildings
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'City':
        """Deserializes city data from a dictionary for loading."""
        city = cls()
        city.credits = data.get("credits", INITIAL_CREDITS)
        city.population = data.get("population", INITIAL_POPULATION)
        city.ore = data.get("ore", INITIAL_ORE)
        city.current_rank_level = data.get("current_rank_level", 0)
        city.current_rank_name = CITY_RANKS[city.current_rank_level]["name"]

        city.buildings = [] # Clear default buildings if any
        city.grid = [[None for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)] # Reset grid

        for building_data in data.get("buildings", []):
            try:
                building = Building.from_dict(building_data)
                city.buildings.append(building)
                # Populate grid - assumes no load-time collisions from save file
                pos_x, pos_y = building.position
                size_w, size_h = building.size
                for x_offset in range(size_w):
                    for y_offset in range(size_h):
                        if 0 <= pos_x + x_offset < GRID_WIDTH and 0 <= pos_y + y_offset < GRID_HEIGHT:
                             city.grid[pos_x + x_offset][pos_y + y_offset] = building
            except ValueError as e:
                print(f"Warning: Could not load building: {e}")


        city.update_resources() # Recalculate all derived stats
        return city

# Example usage:
if __name__ == "__main__":
    my_city = City()
    print(f"Initial Credits: {my_city.credits}, Rank: {my_city.current_rank_name}")

    success, message = my_city.add_building("SOLAR_PANEL", (0, 0))
    print(message)
    success, message = my_city.add_building("HABITAT_SMALL", (2, 2))
    print(message)

    print(f"Credits: {my_city.credits}")
    my_city.update_resources() # Simulate a game tick
    print(f"Credits after update: {my_city.credits}")
    print(f"Population: {my_city.population}, Capacity: {my_city.max_population_capacity}")
    print(f"Net Power: {my_city.net_power} (Gen: {my_city.total_power_generation}, Con: {my_city.total_power_consumption})")
    print(f"City Value: {my_city.city_value}, Rank: {my_city.current_rank_name}")

    # Test power shortage
    my_city.add_building("HABITAT_SMALL", (5,5))
    my_city.add_building("HABITAT_SMALL", (8,8)) # This should cause power issues with default Solar
    print(f"Credits: {my_city.credits}")
    my_city.update_resources()
    print(f"Net Power after more habitats: {my_city.net_power} (Gen: {my_city.total_power_generation}, Con: {my_city.total_power_consumption})")
    for b in my_city.buildings:
        if "Habitat" in b.name:
            print(f"{b.name} at {b.position} is_operational: {b.is_operational}")
    print(f"Population: {my_city.population}, Capacity: {my_city.max_population_capacity}")


    save_data = my_city.to_dict()
    # print("\nSave data:", save_data)

    loaded_city = City.from_dict(save_data)
    print(f"\nLoaded City Credits: {loaded_city.credits}, Rank: {loaded_city.current_rank_name}")
    print(f"Loaded Net Power: {loaded_city.net_power} (Gen: {loaded_city.total_power_generation}, Con: {loaded_city.total_power_consumption})")
    print(f"Loaded Population: {loaded_city.population}, Capacity: {loaded_city.max_population_capacity}")
    for b in loaded_city.buildings:
        print(f"- Loaded {b.name} at {b.position}, Operational: {b.is_operational}")

    success, message = my_city.remove_building((2,2))
    print(message)
    my_city.update_resources()
    print(f"Credits after removal: {my_city.credits}")
    print(f"Net Power after removal: {my_city.net_power}")
