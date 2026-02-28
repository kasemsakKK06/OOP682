import pygame
import os
from .tileset import Tileset
from .map_layer import MapLayer, EMPTY_TILE
from . import map_data

TILE_SIZE = 32


class GameMap:
    def __init__(
        self,
        tileset_path: str,
        grass_grid: list[list[int]],
        path_grid: list[list[int]],
        item_grid: list[list[int]],
        item_images: dict[int, pygame.Surface] | None = None,
    ):
        self.tileset = Tileset(tileset_path, TILE_SIZE, TILE_SIZE)
        self.layer_grass = MapLayer(grass_grid, self.tileset)
        self.layer_path = MapLayer(path_grid, self.tileset)
        self.layer_item = MapLayer(item_grid, self.tileset)
        self.item_images: dict[int, pygame.Surface] = item_images or {}

        self.tile_size = TILE_SIZE
        self.map_cols = len(grass_grid[0]) if grass_grid else 20
        self.map_rows = len(grass_grid) if grass_grid else 20
        self.pixel_width = self.map_cols * TILE_SIZE
        self.pixel_height = self.map_rows * TILE_SIZE

    def draw(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        self.layer_grass.draw(surface, offset_x, offset_y)
        self.layer_path.draw(surface, offset_x, offset_y)
        self._draw_item_layer(surface, offset_x, offset_y)

    def _draw_item_layer(self, surface: pygame.Surface, offset_x: int, offset_y: int):
        for row in range(self.layer_item.rows):
            for col in range(self.layer_item.cols):
                tile_id = self.layer_item.get_tile_id(col, row)
                if tile_id == EMPTY_TILE:
                    continue
                x = col * self.tile_size + offset_x
                y = row * self.tile_size + offset_y
                if tile_id in self.item_images:
                    img = self.item_images[tile_id]
                    img_scaled = pygame.transform.scale(
                        img, (self.tile_size, self.tile_size)
                    )
                    surface.blit(img_scaled, (x, y))
                else:
                    color = {
                        map_data.PORTAL: (180, 0, 220),
                        map_data.TROPHY: (255, 215, 0),
                        map_data.TREE: (0, 255, 0),  # Placeholder for tree
                    }.get(tile_id, (255, 0, 0))
                    pygame.draw.rect(
                        surface, color, (x, y, self.tile_size, self.tile_size)
                    )

    def get_item_at(self, pixel_x: int, pixel_y: int) -> int:
        col = pixel_x // self.tile_size
        row = pixel_y // self.tile_size
        return self.layer_item.get_tile_id(col, row)

    def has_portal(self, pixel_x: int, pixel_y: int) -> bool:
        return self.get_item_at(pixel_x, pixel_y) == map_data.PORTAL

    def has_trophy(self, pixel_x: int, pixel_y: int) -> bool:
        return self.get_item_at(pixel_x, pixel_y) == map_data.TROPHY

    def remove_item_at(self, pixel_x: int, pixel_y: int):
        col = pixel_x // self.tile_size
        row = pixel_y // self.tile_size
        if 0 <= row < self.layer_item.rows and 0 <= col < self.layer_item.cols:
            self.layer_item.grid[row][col] = EMPTY_TILE

    @classmethod
    def create_forest_map(
        cls, base_dir: str, item_images: dict | None = None
    ) -> "GameMap":
        tileset_path = os.path.join(base_dir, "assets", "maps", "forest_tileset.png")
        return cls(
            tileset_path,
            map_data.MAP1_GRASS,
            map_data.MAP1_PATH,
            map_data.MAP1_ITEM,
            item_images,
        )

    @classmethod
    def create_space_map(
        cls, base_dir: str, item_images: dict | None = None
    ) -> "GameMap":
        tileset_path = os.path.join(base_dir, "assets", "maps", "space_tileset.png")
        return cls(
            tileset_path,
            map_data.MAP2_GRASS,
            map_data.MAP2_PATH,
            map_data.MAP2_ITEM,
            item_images,
        )
