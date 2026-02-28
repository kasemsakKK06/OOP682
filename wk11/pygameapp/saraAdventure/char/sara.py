import pygame
from pygame.sprite import Sprite


class Hero(Sprite):
    def __init__(self, name, filename, x, y, map_width=640, map_height=640):
        super().__init__()
        self.name = name

        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
            # Handle background transparency dynamically by sampling top-left pixel
            bg_color = self.sheet.get_at((0, 0))
            self.sheet.set_colorkey(bg_color)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            self.sheet = pygame.Surface((3 * 32, 4 * 32))  # fallback
            self.sheet.fill((255, 0, 255))
            self.sheet.set_colorkey((255, 0, 255))

        sheet_w, sheet_h = self.sheet.get_size()

        # Assume standard 3 cols (animation frames), 4 rows (directions)
        self.cols = 3
        self.rows = 4
        self.frame_width = sheet_w // self.cols
        self.frame_height = sheet_h // self.rows

        self.row = 0  # 0: down, 1: left, 2: right, 3: up
        self.col = 0
        self.elapsed_time = 0

        # logical size in game (tile size)
        self.rect = pygame.Rect(x, y, 32, 32)

        self.map_width = map_width
        self.map_height = map_height
        self.speed = 5

    def update(self, elapsed_time):
        self.elapsed_time += elapsed_time
        if self.elapsed_time > 100:  # ~10fps animation
            self.col = (self.col + 1) % self.cols
            self.elapsed_time = 0

    def left(self):
        self.rect.x -= self.speed
        self.row = 1
        if self.rect.left < 0:
            self.rect.left = 0

    def right(self):
        self.rect.x += self.speed
        self.row = 2
        if self.rect.right > self.map_width:
            self.rect.right = self.map_width

    def up(self):
        self.rect.y -= self.speed
        self.row = 3
        if self.rect.top < 0:
            self.rect.top = 0

    def down(self):
        self.rect.y += self.speed
        self.row = 0
        if self.rect.bottom > self.map_height:
            self.rect.bottom = self.map_height

    def draw(self, surface):
        # Extract correct frame
        frame_rect = pygame.Rect(
            self.col * self.frame_width,
            self.row * self.frame_height,
            self.frame_width,
            self.frame_height,
        )

        # Copy and scale to fit 32x32 hit box
        frame = self.sheet.subsurface(frame_rect).copy()
        frame_scaled = pygame.transform.scale(frame, (32, 32))

        surface.blit(frame_scaled, self.rect)
