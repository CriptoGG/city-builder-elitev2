# Elite 1984 City Builder - Main Game File

import pygame as pg
import os # For sound file paths

from city_builder.city import City
from city_builder.ui import UIManager
from city_builder.sound import SoundManager
from city_builder.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE, BLACK, BUILDING_SPECS, WHITE
)
from city_builder.save_load import save_game, load_game

# Helper function to get asset paths
def get_asset_path(*path_segments):
    base_dir = os.path.dirname(__file__) # Directory of main.py
    return os.path.join(base_dir, "assets", *path_segments)


def main():
    pg.init()
    pg.mixer.pre_init(44100, -16, 2, 512) # Initialize mixer with good defaults
    pg.mixer.init() # Initialize mixer

    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("Elite City Builder")
    clock = pg.time.Clock()

    city = City()
    ui_manager = UIManager(screen, city)
    sound_manager = SoundManager()

    # Load sounds (paths are relative to the assets folder)
    sound_manager.load_sound("ui_click", get_asset_path("sounds", "ui_click.wav"))
    sound_manager.load_sound("build_place", get_asset_path("sounds", "build_place.wav"))
    sound_manager.load_sound("error", get_asset_path("sounds", "error.wav")) # Example error sound

    # Game state variables
    running = True
    game_tick_timer = 0
    time_per_tick = 1000  # ms, so 1 game update per second

    # For displaying messages briefly
    message_display_timer = 0
    message_text = ""
    MESSAGE_DURATION = 3000 # 3 seconds

    # Patch city grid dimensions into UIManager.city instance for ghost placement checks
    # This is a bit of a workaround because UIManager doesn't have direct access to config.GRID_WIDTH/HEIGHT
    # and City's grid is initialized with these.
    # A cleaner way might be to pass GRID_WIDTH/HEIGHT to UIManager or have City expose them.
    city.grid_width = SCREEN_WIDTH // TILE_SIZE
    city.grid_height = (SCREEN_HEIGHT - 80) // TILE_SIZE # UI panel height

    while running:
        dt = clock.tick(60)  # Delta time in milliseconds, cap at 60 FPS
        game_tick_timer += dt
        if message_text and message_display_timer > 0:
            message_display_timer -= dt
            if message_display_timer <= 0:
                message_text = ""


        mouse_pos = pg.mouse.get_pos()
        mouse_grid_pos = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if ui_manager.build_menu_active:
                        ui_manager.toggle_build_menu()
                        sound_manager.play("ui_click")
                    else:
                        ui_manager.selected_building_type = None # Cancel placement
                        sound_manager.play("ui_click")
                elif event.key == pg.K_b:
                    ui_manager.toggle_build_menu()
                    sound_manager.play("ui_click")
                elif event.key == pg.K_s and pg.key.get_mods() & pg.KMOD_CTRL: # Ctrl+S to Save
                    if save_game(city):
                        message_text = "Game Saved!"
                        message_display_timer = MESSAGE_DURATION
                    else:
                        message_text = "Error Saving Game!"
                        message_display_timer = MESSAGE_DURATION
                elif event.key == pg.K_l and pg.key.get_mods() & pg.KMOD_CTRL: # Ctrl+L to Load
                    loaded_c = load_game()
                    if loaded_c:
                        city = loaded_c
                        # Re-patch grid dimensions for the new city instance
                        city.grid_width = SCREEN_WIDTH // TILE_SIZE
                        city.grid_height = (SCREEN_HEIGHT - 80) // TILE_SIZE
                        ui_manager.city = city # Update UIManager's reference
                        message_text = "Game Loaded!"
                        message_display_timer = MESSAGE_DURATION
                    else:
                        message_text = "Error Loading Game or No Save!"
                        message_display_timer = MESSAGE_DURATION


            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if ui_manager.build_menu_active:
                        clicked_on_menu_item = ui_manager.handle_click_build_menu(mouse_pos)
                        if clicked_on_menu_item : # Includes selecting an item or closing
                             sound_manager.play("ui_click")
                    elif ui_manager.selected_building_type:
                        # Check if mouse is within the game grid area (not on the bottom UI panel)
                        if mouse_grid_pos[1] < city.grid_height : # grid_height is number of rows
                            success, msg = city.add_building(ui_manager.selected_building_type, mouse_grid_pos)
                            message_text = msg
                            message_display_timer = MESSAGE_DURATION
                            if success:
                                sound_manager.play("build_place")
                                # Optionally, keep selected_building_type to place multiple
                                # ui_manager.selected_building_type = None
                            else:
                                sound_manager.play("error")
                        else:
                            message_text = "Cannot build on UI panel area."
                            message_display_timer = MESSAGE_DURATION
                            sound_manager.play("error")
                    else: # No menu, no building selected - potentially for selecting existing building later
                        pass
                elif event.button == 3: # Right click - for cancelling placement or deleting
                    if ui_manager.selected_building_type:
                        ui_manager.selected_building_type = None # Cancel placement
                        sound_manager.play("ui_click")
                    else: # Try to remove building
                        # Check if mouse is within the game grid area
                        if mouse_grid_pos[1] < city.grid_height:
                            success, msg = city.remove_building(mouse_grid_pos)
                            message_text = msg
                            message_display_timer = MESSAGE_DURATION
                            if success:
                                sound_manager.play("ui_click") # Or a dedicated "sell/destroy" sound
                            else:
                                sound_manager.play("error")


        # Game logic updates (once per second)
        if game_tick_timer >= time_per_tick:
            city.update_resources()
            game_tick_timer -= time_per_tick # Reset timer for next tick

        # Drawing
        screen.fill(BLACK)

        current_ghost_spec = None
        if ui_manager.selected_building_type:
            current_ghost_spec = BUILDING_SPECS.get(ui_manager.selected_building_type)

        ui_manager.draw(mouse_grid_pos, current_ghost_spec)

        # Display messages (like save/load status, errors)
        if message_text and message_display_timer > 0:
            font = pg.font.Font(None, 28)
            text_surf = font.render(message_text, True, WHITE, (50,50,50)) # White text, grey background
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)) # Above main UI panel
            if ui_manager.build_menu_active: # Move message up if build menu is active
                 text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, 30))
            screen.blit(text_surf, text_rect)


        pg.display.flip()

    pg.quit()

if __name__ == '__main__':
    main()
