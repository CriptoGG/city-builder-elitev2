# Elite 1984 City Builder - Configuration File

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game settings
INITIAL_CREDITS = 10000
INITIAL_POWER = 100
INITIAL_POPULATION = 0
INITIAL_ORE = 500

TILE_SIZE = 32 # pixels
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = (SCREEN_HEIGHT - 100) // TILE_SIZE # Reserve space for UI

# Game progression
CITY_RANKS = {
    0: {"name": "Outpost", "value_needed": 0},
    1: {"name": "Hamlet", "value_needed": 5000},
    2: {"name": "Village", "value_needed": 20000},
    3: {"name": "Town", "value_needed": 100000},
    4: {"name": "City", "value_needed": 500000},
    5: {"name": "Metropolis", "value_needed": 2000000},
}

# Building types - will be expanded
BUILDING_SPECS = {
    "SOLAR_PANEL": {
        "name": "Solar Panel",
        "cost": 500,
        "power_gen": 50, # Generates power
        "power_con": 0,  # Consumes power
        "size": (1, 1), # Grid units
        "char": "S", # Character for simple map display
        "unlock_rank": 0,
        "value": 300,
    },
    "HABITAT_SMALL": {
        "name": "Small Habitat",
        "cost": 1000,
        "power_gen": 0,
        "power_con": 10,
        "population_cap": 50,
        "size": (2, 2),
        "char": "H",
        "unlock_rank": 0,
        "value": 800,
    },
    "ORE_MINE_BASIC": {
        "name": "Basic Ore Mine",
        "cost": 1500,
        "power_gen": 0,
        "power_con": 20, # Consumes power to operate
        "ore_prod": 5,   # Produces 5 ore per tick when operational
        "size": (2, 2),
        "char": "M",
        "unlock_rank": 1, # Unlocks a bit later
        "value": 1000,
    },
    # More buildings to be added here
}
