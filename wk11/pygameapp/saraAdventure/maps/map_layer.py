# maps/map_layer.py
import pygame
from typing import List, Tuple
from .tileset import Tileset

EMPTY_TILE = -1


class MapLayer:
    def __init__(self, grid: List[List[int]], tileset: Tileset):
        """
        Create a map layer.
        :param grid: 2D list of tile indices (row-major).
        :param tileset: Tileset object containing loaded tile images.
        """
        self.grid = [list(row) for row in grid]
        self.tileset = tileset
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0

    def get_tile_id(self, col: int, row: int) -> int:
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return EMPTY_TILE

    def draw(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """
        Draw the layer onto the given surface.
        """
        for row_idx, row in enumerate(self.grid):
            for col_idx, tile_id in enumerate(row):
                if tile_id == EMPTY_TILE:
                    continue

                # Get the pre-sliced tile surface from Tileset
                tile_img = self.tileset.get(tile_id)
                if tile_img:
                    dest_x = offset_x + col_idx * self.tileset.tile_width
                    dest_y = offset_y + row_idx * self.tileset.tile_height
                    surface.blit(tile_img, (dest_x, dest_y))
