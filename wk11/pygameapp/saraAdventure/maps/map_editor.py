import pygame
import sys
import os
import json
import random

# ================= CONFIG =================
TILE_SIZE = 32
GRID_SIZE = 15  # Changed from 15 to 25
MAP_WIDTH = TILE_SIZE * GRID_SIZE
MAP_HEIGHT = TILE_SIZE * GRID_SIZE

PANEL_WIDTH = 300  # ด้านขวาไว้โชว์ tileset
SCREEN_WIDTH = MAP_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = MAP_HEIGHT

MODES = {
    "forest": {
        "map_file": os.path.join("map", "forest_map.json"),
        "tileset_path": os.path.join("assets", "maps", "forest_tileset.png"),
    },
    "space": {
        "map_file": os.path.join("map", "space_map.json"),
        "tileset_path": os.path.join("assets", "maps", "space_tileset.png"),
    },
}


class MapEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Advanced Map Editor")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 22)

        self.current_mode = "forest"
        self.selected_tile = 0
        self.current_layer_index = 0
        self.panel_scroll = 0  # For scrolling the right panel

        self.load_tileset()
        self.layers = self.load_map()

    def load_tileset(self):
        tileset_path = MODES[self.current_mode]["tileset_path"]
        if not os.path.exists(tileset_path):
            print(f"Warning: Tileset {tileset_path} not found.")
            self.tileset = pygame.Surface((3 * 32, 3 * 32))
            self.tileset.fill((255, 0, 255))
        else:
            self.tileset = pygame.image.load(tileset_path).convert_alpha()

        self.tileset_cols = self.tileset.get_width() // TILE_SIZE
        self.tileset_rows = self.tileset.get_height() // TILE_SIZE
        self.total_tiles = self.tileset_cols * self.tileset_rows

    def toggle_mode(self):
        self.save_map()  # Save current progress
        if self.current_mode == "forest":
            self.current_mode = "space"
        else:
            self.current_mode = "forest"

        self.load_tileset()
        self.layers = self.load_map()
        self.selected_tile = 0
        print(f"Switched to {self.current_mode} mode")

    # ================= MAP =================

    def load_map(self):
        map_file = MODES[self.current_mode]["map_file"]
        layers = []
        if os.path.exists(map_file):
            with open(map_file, "r") as f:
                layers = json.load(f).get("layers", [])

        if not layers:
            layers = [
                {
                    "name": "ground",
                    "grid": [[-1] * GRID_SIZE for _ in range(GRID_SIZE)],
                },
                {"name": "path", "grid": [[-1] * GRID_SIZE for _ in range(GRID_SIZE)]},
                {"name": "items", "grid": [[-1] * GRID_SIZE for _ in range(GRID_SIZE)]},
            ]

        # Ensure 'events' layer exists
        if not any(l["name"] == "events" for l in layers):
            layers.append(
                {"name": "events", "grid": [[-1] * GRID_SIZE for _ in range(GRID_SIZE)]}
            )

        # Resize grids if GRID_SIZE changed
        for layer in layers:
            old_grid = layer["grid"]
            new_grid = [[-1] * GRID_SIZE for _ in range(GRID_SIZE)]
            for y in range(min(GRID_SIZE, len(old_grid))):
                for x in range(min(GRID_SIZE, len(old_grid[y]))):
                    new_grid[y][x] = old_grid[y][x]
            layer["grid"] = new_grid

        return layers

    def save_map(self):
        map_file = MODES[self.current_mode]["map_file"]
        os.makedirs(os.path.dirname(map_file), exist_ok=True)
        with open(map_file, "w") as f:
            json.dump({"layers": self.layers}, f, indent=4)
        print(f"Map Saved to {map_file}!")

    # ================= TILE =================

    def get_tile(self, index):
        if index < 0:
            return None
        if index == 998:  # Special dark green tile for "spawn point" / "editable point"
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0, 100, 0))
            return s
        if index == 999:  # Special red tile for "next level"
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((255, 0, 0))
            return s

        x = (index % self.tileset_cols) * TILE_SIZE
        y = (index // self.tileset_cols) * TILE_SIZE
        if (
            y >= self.tileset.get_height()
            or x >= self.tileset.get_width()
            or y < 0
            or x < 0
        ):
            return None
        return self.tileset.subsurface((x, y, TILE_SIZE, TILE_SIZE))

    # ================= DRAW =================

    def draw_grid(self):
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(
                self.screen,
                (80, 80, 80),
                (i * TILE_SIZE, 0),
                (i * TILE_SIZE, MAP_HEIGHT),
            )
            pygame.draw.line(
                self.screen,
                (80, 80, 80),
                (0, i * TILE_SIZE),
                (MAP_WIDTH, i * TILE_SIZE),
            )

    def draw_layers(self):
        for layer in self.layers:
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    tile = layer["grid"][y][x]
                    if tile != -1:
                        self.screen.blit(
                            self.get_tile(tile), (x * TILE_SIZE, y * TILE_SIZE)
                        )

    def draw_tileset_panel(self):
        panel_x = MAP_WIDTH
        self.screen.fill((30, 30, 30), (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT))

        COLS = 7
        for i in range(self.total_tiles):
            tile = self.get_tile(i)
            if not tile:
                continue
            col = i % COLS
            row = i // COLS
            x = panel_x + col * (TILE_SIZE + 5) + 10
            y = row * (TILE_SIZE + 5) + 10 - self.panel_scroll

            if y + TILE_SIZE > 0 and y < SCREEN_HEIGHT:
                self.screen.blit(tile, (x, y))

            if i == self.selected_tile:
                pygame.draw.rect(
                    self.screen, (255, 255, 0), (x, y, TILE_SIZE, TILE_SIZE), 3
                )

        # Draw next level tile (Red)
        next_level_idx = 999
        tile = self.get_tile(next_level_idx)
        col = self.total_tiles % COLS
        row = self.total_tiles // COLS
        x = panel_x + col * (TILE_SIZE + 5) + 10
        y = row * (TILE_SIZE + 5) + 10 - self.panel_scroll
        if y + TILE_SIZE > 0 and y < SCREEN_HEIGHT:
            self.screen.blit(tile, (x, y))

        if next_level_idx == self.selected_tile:
            pygame.draw.rect(
                self.screen, (255, 255, 0), (x, y, TILE_SIZE, TILE_SIZE), 3
            )

        # Draw dark green tile
        spawn_point_idx = 998
        tile_green = self.get_tile(spawn_point_idx)
        col_green = (self.total_tiles + 1) % COLS
        row_green = (self.total_tiles + 1) // COLS
        x_green = panel_x + col_green * (TILE_SIZE + 5) + 10
        y_green = row_green * (TILE_SIZE + 5) + 10 - self.panel_scroll
        if y_green + TILE_SIZE > 0 and y_green < SCREEN_HEIGHT:
            self.screen.blit(tile_green, (x_green, y_green))

        if spawn_point_idx == self.selected_tile:
            pygame.draw.rect(
                self.screen, (255, 255, 0), (x_green, y_green, TILE_SIZE, TILE_SIZE), 3
            )

    def generate_random(self):
        ground = self.layers[0]["grid"]
        path = self.layers[1]["grid"]
        items = self.layers[2]["grid"]
        events = self.layers[3]["grid"] if len(self.layers) > 3 else None

        if self.current_mode == "forest":
            GRASS = [0, 1, 2]
            TREE, PATH, ROCK, BUSH = 5, 6, 8, 9
            WALL_TILE = TREE
        else:
            GRASS = [0, 1]
            TREE, PATH, ROCK, BUSH = 4, 2, 4, -1
            WALL_TILE = 4

        # 1) Clear all layers
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                ground[y][x] = random.choice(GRASS)
                path[y][x] = -1
                items[y][x] = -1
                if events:
                    events[y][x] = -1

        # 2) Place border walls
        for i in range(GRID_SIZE):
            ground[0][i] = WALL_TILE
            ground[GRID_SIZE - 1][i] = WALL_TILE
            ground[i][0] = WALL_TILE
            ground[i][GRID_SIZE - 1] = WALL_TILE

        # 3) Build a connected path from top to bottom
        #    Track which cells are part of the path
        path_cells = set()
        cx = GRID_SIZE // 2
        for y in range(1, GRID_SIZE - 1):
            path[y][cx] = PATH
            path_cells.add((cx, y))
            if random.random() < 0.5:
                new_x = cx + random.choice([-1, 1])
                new_x = max(1, min(GRID_SIZE - 2, new_x))
                # Fill the horizontal segment so the path stays connected
                step = 1 if new_x > cx else -1
                for fill_x in range(cx, new_x + step, step):
                    path[y][fill_x] = PATH
                    path_cells.add((fill_x, y))
                cx = new_x

        # 4) Place items only on tiles NOT on or adjacent to the path
        for _ in range(20):
            rx = random.randint(1, GRID_SIZE - 2)
            ry = random.randint(1, GRID_SIZE - 2)
            # Skip if on path or next to path
            too_close = False
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    if (rx + dx, ry + dy) in path_cells:
                        too_close = True
                        break
                if too_close:
                    break
            if too_close:
                continue
            # Skip border walls
            if ground[ry][rx] == WALL_TILE:
                continue
            choices = [ROCK]
            if BUSH != -1:
                choices.append(BUSH)
            items[ry][rx] = random.choice(choices)

    # ================= MAIN LOOP =================

    def run(self):
        painting = False
        erasing = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.save_map()
                    if event.key == pygame.K_1:
                        self.current_layer_index = 0
                    if event.key == pygame.K_2:
                        self.current_layer_index = 1
                    if event.key == pygame.K_3:
                        self.current_layer_index = 2
                    if event.key == pygame.K_4:
                        self.current_layer_index = 3
                    if event.key == pygame.K_c:
                        self.clear_layer()
                    if event.key == pygame.K_g:
                        self.generate_random()
                    if event.key == pygame.K_m:
                        self.toggle_mode()
                    # Keyboard scrolling as fallback
                    if event.key == pygame.K_UP:
                        self.panel_scroll = max(0, self.panel_scroll - 50)
                    if event.key == pygame.K_DOWN:
                        self.panel_scroll += 50

                if event.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    if mx >= MAP_WIDTH:  # Only scroll when mouse is in panel
                        self.panel_scroll = max(0, self.panel_scroll - event.y * 30)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        mx, my = event.pos
                        if mx >= MAP_WIDTH:
                            self.handle_panel_click(mx, my)
                        else:
                            painting = True
                            self.handle_map_paint(mx, my, True, False)
                    elif event.button == 3:
                        mx, my = event.pos
                        if mx < MAP_WIDTH:
                            erasing = True
                            self.handle_map_paint(mx, my, False, True)

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        painting = False
                    if event.button == 3:
                        erasing = False

                if event.type == pygame.MOUSEMOTION:
                    if painting or erasing:
                        mx, my = event.pos
                        if mx < MAP_WIDTH:
                            self.handle_map_paint(mx, my, painting, erasing)

            self.screen.fill((50, 50, 50))
            self.draw_layers()
            self.draw_grid()
            self.draw_tileset_panel()

            layer_name = self.layers[self.current_layer_index]["name"]
            text_str = f"Mode: {self.current_mode.title()} | Layer: {layer_name} | Tile: {self.selected_tile} | M=Toggle | S=Save | C=Clear | G=Gen"
            text = self.font.render(
                text_str,
                True,
                (255, 255, 255),
            )
            self.screen.blit(text, (10, SCREEN_HEIGHT - 25))

            pygame.display.flip()
            self.clock.tick(60)

    # ================= INPUT =================

    def handle_map_paint(self, mx, my, painting, erasing):
        gx = mx // TILE_SIZE
        gy = my // TILE_SIZE
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            if painting:
                self.layers[self.current_layer_index]["grid"][gy][
                    gx
                ] = self.selected_tile
            elif erasing:
                self.layers[self.current_layer_index]["grid"][gy][gx] = -1

    def handle_panel_click(self, mx, my):
        COLS = 7
        local_x = mx - MAP_WIDTH
        col = (local_x - 10) // (TILE_SIZE + 5)
        row = (my - 10 + self.panel_scroll) // (TILE_SIZE + 5)
        if 0 <= col < COLS:
            index = row * COLS + col
            if 0 <= index < self.total_tiles:
                self.selected_tile = index
            elif index == self.total_tiles:
                self.selected_tile = 999
            elif index == self.total_tiles + 1:
                self.selected_tile = 998

    def clear_layer(self):
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                self.layers[self.current_layer_index]["grid"][y][x] = -1


if __name__ == "__main__":
    MapEditor().run()
