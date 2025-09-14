import os
import importlib.util
import sys
from .ui import draw_menu, MAX_MENU_ITEMS

class GameMode:
    def __init__(self, device, roms_dir):
        self.device = device
        self.name = "GAME"
        self.roms_dir = roms_dir
        self.game_files = []
        self.selected_game_index = 0
        self.menu_scroll_offset = 0
        self.running_game_module = None
        self.page_index = 0
        self.pages = ["GAMES"]

    def is_game_running(self):
        return self.running_game_module is not None

    def handle_input(self, key):
        if self.running_game_module:
            if self.running_game_module.handle_input(key) == False:
                game_name = os.path.splitext(os.path.basename(self.game_files[self.selected_game_index]))[0]
                module_name = "roms." + game_name
                if module_name in sys.modules:
                    del sys.modules[module_name]
                self.running_game_module = None
            return

        page_name = self.pages[self.page_index]
        if page_name == "GAMES":
            self.handle_games_page_input(key)

    def handle_games_page_input(self, key):
        if not self.game_files:
            return

        if key == 'W':
            self.selected_game_index = (self.selected_game_index - 1 + len(self.game_files)) % len(self.game_files)
        elif key == 'S':
            self.selected_game_index = (self.selected_game_index + 1) % len(self.game_files)
        elif key == 'B' or key == 'START':
            if self.game_files:
                selected_game_path = self.game_files[self.selected_game_index]
                game_name = os.path.splitext(os.path.basename(selected_game_path))[0]
                
                try:
                    spec = importlib.util.spec_from_file_location("roms." + game_name, selected_game_path)
                    game_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(game_module)
                    
                    if hasattr(game_module, 'init') and hasattr(game_module, 'handle_input') and hasattr(game_module, 'draw'):
                        game_module.init(self.device)
                        self.running_game_module = game_module
                    else:
                        print(f"Error: Game '{game_name}' is missing required functions (init, handle_input, draw).")

                except Exception as e:
                    print(f"Error loading game: {e}")
        
        if self.selected_game_index < self.menu_scroll_offset:
            self.menu_scroll_offset = self.selected_game_index
        elif self.selected_game_index >= self.menu_scroll_offset + MAX_MENU_ITEMS:
            self.menu_scroll_offset = self.selected_game_index - MAX_MENU_ITEMS + 1

    def draw(self, draw, current_mode_name):
        if self.running_game_module:
            self.running_game_module.draw(draw)
            return

        page_name = self.pages[self.page_index]
        if page_name == "GAMES":
            self.draw_games_page(draw, current_mode_name)

    def draw_games_page(self, draw, current_mode_name):
        display_names = [os.path.splitext(os.path.basename(p))[0] for p in self.game_files]
        draw_menu(draw, "GAMES", display_names, self.selected_game_index, self.menu_scroll_offset)

    def activate(self):
        self.game_files = []
        if os.path.exists(self.roms_dir):
            self.game_files = sorted([os.path.join(self.roms_dir, f) for f in os.listdir(self.roms_dir) if f.endswith('.py') and f != '__init__.py'])
        
        self.menu_scroll_offset = 0
        self.selected_game_index = 0
        self.page_index = 0
        self.running_game_module = None

    def deactivate(self):
        self.running_game_module = None
