# Elite 1984 City Builder - Save/Load Logic

import json
import os
from city_builder.city import City

SAVE_GAME_DIR = "city_builder_saves"
SAVE_GAME_FILENAME = "city_save.json"

def ensure_save_dir_exists():
    """Ensures the save game directory exists."""
    if not os.path.exists(SAVE_GAME_DIR):
        try:
            os.makedirs(SAVE_GAME_DIR)
            print(f"Save directory created: {SAVE_GAME_DIR}")
        except OSError as e:
            print(f"Error creating save directory {SAVE_GAME_DIR}: {e}")
            return False
    return True

def save_game(city: City, filename: str = SAVE_GAME_FILENAME) -> bool:
    """Saves the current city state to a JSON file."""
    if not ensure_save_dir_exists():
        return False

    filepath = os.path.join(SAVE_GAME_DIR, filename)
    try:
        city_data = city.to_dict()
        with open(filepath, 'w') as f:
            json.dump(city_data, f, indent=4)
        print(f"Game saved successfully to {filepath}")
        return True
    except IOError as e:
        print(f"Error saving game to {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during save: {e}")
    return False

def load_game(filename: str = SAVE_GAME_FILENAME) -> City | None:
    """Loads a city state from a JSON file."""
    filepath = os.path.join(SAVE_GAME_DIR, filename)
    if not os.path.exists(filepath):
        print(f"No save file found at {filepath}")
        return None

    try:
        with open(filepath, 'r') as f:
            city_data = json.load(f)

        loaded_city = City.from_dict(city_data)
        print(f"Game loaded successfully from {filepath}")
        return loaded_city
    except IOError as e:
        print(f"Error loading game from {filepath}: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filepath}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during load: {e}")
    return None

# Example usage:
if __name__ == "__main__":
    # Create a dummy city for testing
    test_city = City()
    test_city.add_building("SOLAR_PANEL", (1,1))
    test_city.credits = 5000
    test_city.population = 20
    test_city.update_resources() # Calculate values

    print("--- Testing Save ---")
    save_game(test_city, "test_save.json")

    print("\n--- Testing Load ---")
    loaded_city = load_game("test_save.json")

    if loaded_city:
        print(f"Loaded City Credits: {loaded_city.credits} (Original: {test_city.credits})")
        print(f"Loaded City Population: {loaded_city.population} (Original: {test_city.population})")
        print(f"Loaded City Net Power: {loaded_city.net_power}")
        print(f"Number of buildings loaded: {len(loaded_city.buildings)}")
        if loaded_city.buildings:
            print(f"First loaded building: {loaded_city.buildings[0].name} at {loaded_city.buildings[0].position}")

    print("\n--- Testing Load Non-Existent File ---")
    non_existent_city = load_game("no_such_save.json")
    print(f"Result of loading non-existent file: {non_existent_city}")

    # Clean up test save file
    test_save_path = os.path.join(SAVE_GAME_DIR, "test_save.json")
    if os.path.exists(test_save_path):
        os.remove(test_save_path)
        # print(f"Cleaned up {test_save_path}")
    if os.path.exists(SAVE_GAME_DIR) and not os.listdir(SAVE_GAME_DIR):
        os.rmdir(SAVE_GAME_DIR)
        # print(f"Cleaned up empty directory {SAVE_GAME_DIR}")
