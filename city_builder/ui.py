# Elite 1984 City Builder - UI Rendering Logic

import pygame as pg
from city_builder.config import WHITE, GREEN, RED, YELLOW, BLUE, TILE_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from city_builder.city import City
from city_builder.buildings import Building, get_available_buildings # For build menu

# Basic font
FONT_NAME = None # Default system font
UI_FONT_SIZE = 20
GAME_FONT_SIZE = TILE_SIZE // 2


class UIManager:
    def __init__(self, screen, city: City):
        self.screen = screen
        self.city = city
        self.ui_font = pg.font.Font(FONT_NAME, UI_FONT_SIZE)
        self.game_font = pg.font.Font(FONT_NAME, GAME_FONT_SIZE)

        self.build_menu_active = False
        self.available_buildings_for_menu = []
        self.selected_building_type = None # Stores the type_id like "SOLAR_PANEL"

        # Build menu layout
        self.menu_rect = pg.Rect(50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100)
        self.menu_item_height = 30
        self.menu_close_button_rect = pg.Rect(self.menu_rect.right - 30, self.menu_rect.top, 30, 30)


    def toggle_build_menu(self):
        self.build_menu_active = not self.build_menu_active
        if self.build_menu_active:
            self.available_buildings_for_menu = list(get_available_buildings(self.city.current_rank_level).items())
        else:
            self.selected_building_type = None # Clear selection when closing menu

    def handle_click_build_menu(self, mouse_pos):
        if not self.build_menu_active:
            return False # Menu not active

        if self.menu_close_button_rect.collidepoint(mouse_pos):
            self.toggle_build_menu()
            return True

        # Check item clicks
        for i, (type_id, spec) in enumerate(self.available_buildings_for_menu):
            item_rect = pg.Rect(
                self.menu_rect.left + 10,
                self.menu_rect.top + 30 + (i * self.menu_item_height), # +30 for title/close button
                self.menu_rect.width - 20,
                self.menu_item_height
            )
            if item_rect.collidepoint(mouse_pos):
                self.selected_building_type = type_id
                self.build_menu_active = False # Close menu on selection
                # print(f"Selected building: {self.selected_building_type}")
                return True
        return False # Click was in menu area but not on an item/close

    def draw_build_menu(self):
        if not self.build_menu_active:
            return

        # Menu background
        pg.draw.rect(self.screen, (30, 30, 30), self.menu_rect) # Dark grey
        pg.draw.rect(self.screen, WHITE, self.menu_rect, 1) # Border

        # Title
        title_surf = self.ui_font.render("Build Menu", True, WHITE)
        self.screen.blit(title_surf, (self.menu_rect.left + 10, self.menu_rect.top + 5))

        # Close button
        pg.draw.rect(self.screen, RED, self.menu_close_button_rect)
        close_text = self.ui_font.render("X", True, WHITE)
        self.screen.blit(close_text, (self.menu_close_button_rect.x + 8, self.menu_close_button_rect.y + 3))


        # Menu items
        for i, (type_id, spec) in enumerate(self.available_buildings_for_menu):
            item_y = self.menu_rect.top + 30 + (i * self.menu_item_height)
            item_rect = pg.Rect(
                self.menu_rect.left + 10,
                item_y,
                self.menu_rect.width - 20,
                self.menu_item_height
            )

            # Highlight on hover (basic)
            mouse_pos = pg.mouse.get_pos()
            if item_rect.collidepoint(mouse_pos):
                pg.draw.rect(self.screen, (80, 80, 80), item_rect)


            text = f"{spec['name']} (Cost: {spec['cost']}, Pwr: {spec.get('power_gen',0)-spec.get('power_con',0)})"
            surf = self.ui_font.render(text, True, WHITE if self.city.credits >= spec['cost'] else RED)
            self.screen.blit(surf, (item_rect.left + 5, item_y + 5))


    def draw_main_ui(self):
        """Draws the main game UI (resource display, city rank, etc.)"""
        ui_panel_height = 80
        ui_panel_rect = pg.Rect(0, SCREEN_HEIGHT - ui_panel_height, SCREEN_WIDTH, ui_panel_height)
        pg.draw.rect(self.screen, (10, 10, 30), ui_panel_rect) # Dark blue panel
        pg.draw.line(self.screen, WHITE, (0, SCREEN_HEIGHT - ui_panel_height), (SCREEN_WIDTH, SCREEN_HEIGHT - ui_panel_height), 1)

        y_offset = SCREEN_HEIGHT - ui_panel_height + 5
        x_offset = 10

        # Credits
        credits_text = f"Credits: {self.city.credits}"
        credits_surf = self.ui_font.render(credits_text, True, GREEN)
        self.screen.blit(credits_surf, (x_offset, y_offset))
        x_offset += credits_surf.get_width() + 20

        # Population
        pop_text = f"Pop: {self.city.population} / {self.city.max_population_capacity}"
        pop_surf = self.ui_font.render(pop_text, True, YELLOW)
        self.screen.blit(pop_surf, (x_offset, y_offset))
        x_offset += pop_surf.get_width() + 20

        # Power
        power_color = GREEN if self.city.net_power >= 0 else RED
        power_text = f"Power: {self.city.net_power} (G:{self.city.total_power_generation} C:{self.city.total_power_consumption})"
        power_surf = self.ui_font.render(power_text, True, power_color)
        self.screen.blit(power_surf, (x_offset, y_offset))
        x_offset += power_surf.get_width() + 20

        # Ore
        ore_text = f"Ore: {self.city.ore}" # Placeholder
        ore_surf = self.ui_font.render(ore_text, True, (150, 150, 150)) # Grey
        self.screen.blit(ore_surf, (x_offset, y_offset))

        # Second line for UI
        y_offset += UI_FONT_SIZE + 5
        x_offset = 10

        # City Rank
        rank_text = f"Rank: {self.city.current_rank_name} (Val: {self.city.city_value})"
        rank_surf = self.ui_font.render(rank_text, True, WHITE)
        self.screen.blit(rank_surf, (x_offset, y_offset))
        x_offset += rank_surf.get_width() + 20

        # Build button (placeholder text)
        build_button_text = "[B]uild Menu"
        build_surf = self.ui_font.render(build_button_text, True, WHITE)
        self.screen.blit(build_surf, (SCREEN_WIDTH - build_surf.get_width() - 10, SCREEN_HEIGHT - ui_panel_height + 5))

        # Message line (for errors or info)
        # self.message_line = "" # This would be set by game logic
        # if hasattr(self, 'message_line') and self.message_line:
        #    msg_surf = self.ui_font.render(self.message_line, True, RED)
        #    self.screen.blit(msg_surf, (x_offset, y_offset))


    def draw_grid(self):
        """Draws the construction grid."""
        grid_surface_height = SCREEN_HEIGHT - 80 # Height of the UI panel
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            pg.draw.line(self.screen, (50, 50, 50), (x, 0), (x, grid_surface_height), 1) # Dim grid lines
        for y in range(0, grid_surface_height, TILE_SIZE):
            pg.draw.line(self.screen, (50, 50, 50), (0, y), (SCREEN_WIDTH, y), 1)


    def draw_buildings(self):
        """Draws wireframe representations of buildings."""
        for building in self.city.buildings:
            rect_color = GREEN if building.is_operational else RED

            # Main building rectangle
            base_x = building.position[0] * TILE_SIZE
            base_y = building.position[1] * TILE_SIZE
            width_px = building.size[0] * TILE_SIZE
            height_px = building.size[1] * TILE_SIZE

            building_rect = pg.Rect(base_x, base_y, width_px, height_px)

            if building.type == "SOLAR_PANEL" and building.size == (1,1) :
                # Make 1x1 solar panels appear flatter and add a line
                panel_rect = pg.Rect(base_x, base_y + height_px // 3, width_px, height_px // 3)
                pg.draw.rect(self.screen, rect_color, panel_rect, 1)
                # Add a diagonal line to suggest a panel surface for 1x1 solar
                pg.draw.line(self.screen, rect_color,
                             (panel_rect.left + 2, panel_rect.top + 2),
                             (panel_rect.right - 2, panel_rect.bottom - 2), 1)
            else:
                # Default wireframe box for other buildings or larger solar panels
                pg.draw.rect(self.screen, rect_color, building_rect, 1)

            # Draw character in the center of the first tile of the building
            char_surf = self.game_font.render(building.char, True, rect_color)
            # Position character relative to the top-left of the building's first tile
            char_rect = char_surf.get_rect(center=(base_x + TILE_SIZE / 2, base_y + TILE_SIZE / 2))
            self.screen.blit(char_surf, char_rect)

    def draw_selected_building_ghost(self, mouse_grid_pos, building_spec):
        """Draws a ghost of the building to be placed at the mouse cursor."""
        if not building_spec or not mouse_grid_pos:
            return

        ghost_color = BLUE # Indicates placement mode
        width, height = building_spec["size"]

        ghost_rect = pg.Rect(
            mouse_grid_pos[0] * TILE_SIZE,
            mouse_grid_pos[1] * TILE_SIZE,
            width * TILE_SIZE,
            height * TILE_SIZE
        )

        # Check for collision for ghost color
        can_place = True
        # Check grid boundaries and collision
        pos_x, pos_y = mouse_grid_pos
        size_w, size_h = building_spec["size"]

        if not (0 <= pos_x < self.city.grid_width and \
                0 <= pos_y < self.city.grid_height and \
                0 <= pos_x + size_w -1 < self.city.grid_width and \
                0 <= pos_y + size_h -1 < self.city.grid_height):
            can_place = False
        else: # Check occupied cells only if within bounds
            for x_offset in range(size_w):
                for y_offset in range(size_h):
                    # Check against city grid, need city.grid_width/height here
                    grid_check_x = pos_x + x_offset
                    grid_check_y = pos_y + y_offset
                    if self.city.grid[grid_check_x][grid_check_y] is not None:
                        can_place = False
                        break
                if not can_place:
                    break

        ghost_color = BLUE if can_place else RED

        # Create a semi-transparent surface for the ghost
        s = pg.Surface((width * TILE_SIZE, height * TILE_SIZE), pg.SRCALPHA)
        s.fill((*ghost_color, 100)) # color with alpha
        self.screen.blit(s, (ghost_rect.left, ghost_rect.top))
        pg.draw.rect(self.screen, ghost_color, ghost_rect, 1) # Outline

    def draw(self, mouse_grid_pos=None, current_ghost_spec=None):
        """Draws all UI elements."""
        self.screen.fill((0,0,0)) # Clear screen (black)
        self.draw_grid()
        self.draw_buildings()
        if self.selected_building_type and current_ghost_spec and mouse_grid_pos:
            self.draw_selected_building_ghost(mouse_grid_pos, current_ghost_spec)
        self.draw_main_ui() # Draw this last so it's on top of game elements near bottom
        self.draw_build_menu() # Drawn on top of everything if active


if __name__ == '__main__':
    # Basic test for UIManager
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("UI Test")

    test_city = City() # Create a dummy city
    test_city.add_building("SOLAR_PANEL", (2,2))
    test_city.add_building("HABITAT_SMALL", (5,5))

    ui_manager = UIManager(screen, test_city)
    ui_manager.city.grid_width = SCREEN_WIDTH // TILE_SIZE # Patch for test
    ui_manager.city.grid_height = (SCREEN_HEIGHT - 80) // TILE_SIZE # Patch for test


    clock = pg.time.Clock()
    running = True
    while running:
        mouse_pos = pg.mouse.get_pos()
        mouse_grid_pos = (mouse_pos[0] // TILE_SIZE, mouse_pos[1] // TILE_SIZE)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_b:
                    ui_manager.toggle_build_menu()
                if event.key == pg.K_ESCAPE:
                    if ui_manager.build_menu_active:
                        ui_manager.toggle_build_menu()
                    else:
                        ui_manager.selected_building_type = None # Cancel placement

            if event.type == pg.MOUSEBUTTONDOWN:
                if ui_manager.build_menu_active:
                    ui_manager.handle_click_build_menu(mouse_pos)
                elif ui_manager.selected_building_type: # If a building is selected for placement
                    # This logic would be in main.py normally
                    # success, msg = test_city.add_building(ui_manager.selected_building_type, mouse_grid_pos)
                    # print(msg)
                    # if success:
                    # ui_manager.selected_building_type = None # Clear after placement
                    print(f"Attempting to place {ui_manager.selected_building_type} at {mouse_grid_pos}")
                    ui_manager.selected_building_type = None # Simulate placement, clear selection
                else: # No menu, no building selected - maybe select building or other action
                    pass


        # Update game state (dummy)
        test_city.update_resources() # Simulate time passing

        # Draw everything
        ghost_spec = None
        if ui_manager.selected_building_type:
            from city_builder.config import BUILDING_SPECS
            ghost_spec = BUILDING_SPECS.get(ui_manager.selected_building_type)

        ui_manager.draw(mouse_grid_pos, ghost_spec)

        pg.display.flip()
        clock.tick(30)

    pg.quit()
