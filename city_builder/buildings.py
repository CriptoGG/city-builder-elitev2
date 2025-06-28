# Elite 1984 City Builder - Buildings Logic

from typing import Tuple, Dict, Any
from city_builder.config import BUILDING_SPECS

class Building:
    """
    Represents a single building in the city.
    """
    def __init__(self, building_type: str, position: Tuple[int, int]):
        if building_type not in BUILDING_SPECS:
            raise ValueError(f"Unknown building type: {building_type}")

        self.spec = BUILDING_SPECS[building_type]
        self.type: str = building_type
        self.name: str = self.spec["name"]
        self.position: Tuple[int, int] = position  # Grid coordinates (x, y)
        self.cost: int = self.spec["cost"]
        self.power_generation: int = self.spec.get("power_gen", 0)
        self.power_consumption: int = self.spec.get("power_con", 0)
        self.population_capacity: int = self.spec.get("population_cap", 0)
        self.ore_production: int = self.spec.get("ore_prod", 0) # Example for future use
        self.size: Tuple[int, int] = self.spec["size"] # (width, height) in grid units
        self.char: str = self.spec["char"]
        self.value: int = self.spec["value"]
        self.is_operational: bool = True # Can be turned off by power shortage

    def __str__(self) -> str:
        return f"{self.name} at {self.position}"

    def get_net_power(self) -> int:
        """Returns the net power (generation - consumption) of the building."""
        if not self.is_operational:
            return 0
        return self.power_generation - self.power_consumption

    def get_population_capacity(self) -> int:
        """Returns the population capacity provided by this building."""
        if not self.is_operational:
            return 0
        return self.population_capacity

    def get_ore_production(self) -> int:
        """Returns the ore production of this building."""
        if not self.is_operational:
            return 0
        return self.ore_production

    def to_dict(self) -> Dict[str, Any]:
        """Serializes building data to a dictionary for saving."""
        return {
            "type": self.type,
            "position_x": self.position[0],
            "position_y": self.position[1],
            "is_operational": self.is_operational, # Save operational state
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Building':
        """Deserializes building data from a dictionary for loading."""
        building = cls(data["type"], (data["position_x"], data["position_y"]))
        building.is_operational = data.get("is_operational", True)
        return building

def get_available_buildings(current_rank: int) -> Dict[str, Dict[str, Any]]:
    """
    Returns a dictionary of building specs that are available at the current city rank.
    """
    available = {}
    for type_id, spec in BUILDING_SPECS.items():
        if spec["unlock_rank"] <= current_rank:
            available[type_id] = spec
    return available

# Example usage:
if __name__ == "__main__":
    solar_panel = Building("SOLAR_PANEL", (5, 5))
    print(solar_panel)
    print(f"Net power: {solar_panel.get_net_power()}")

    habitat = Building("HABITAT_SMALL", (10, 10))
    print(habitat)
    print(f"Net power: {habitat.get_net_power()}")
    print(f"Population capacity: {habitat.get_population_capacity()}")

    print("\nAvailable at rank 0:")
    for b_id, b_spec in get_available_buildings(0).items():
        print(f"- {b_spec['name']}")

    print("\nAvailable at rank 1 (assuming no new buildings for rank 1 yet):")
    for b_id, b_spec in get_available_buildings(1).items():
        print(f"- {b_spec['name']}")
