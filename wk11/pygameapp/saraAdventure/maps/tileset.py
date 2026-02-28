import pygame


class Tileset:
    """โหลด tileset image และแบ่งเป็น tile ย่อย ๆ ตามขนาดที่กำหนด"""

    def __init__(self, filename: str, tile_width: int = 32, tile_height: int = 32):
        """
        Parameters
        ----------
        filename   : path ไปยัง tileset image (PNG)
        tile_width : ความกว้างของ tile แต่ละตัว (pixel)
        tile_height: ความสูงของ tile แต่ละตัว (pixel)
        """
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.tiles: dict[int, pygame.Surface] = {}  # tile_id → Surface

        sheet = pygame.image.load(filename).convert_alpha()
        sheet_width, sheet_height = sheet.get_size()

        cols = sheet_width // tile_width
        rows = sheet_height // tile_height

        tile_id = 0
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(
                    col * tile_width,
                    row * tile_height,
                    tile_width,
                    tile_height,
                )
                self.tiles[tile_id] = sheet.subsurface(rect).copy()
                tile_id += 1

    def get(self, tile_id: int) -> pygame.Surface | None:
        """คืน Surface ของ tile ตาม id, ถ้าไม่มีคืน None"""
        return self.tiles.get(tile_id)

    def __len__(self) -> int:
        return len(self.tiles)
