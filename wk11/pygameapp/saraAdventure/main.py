import sys, os
import pygame

from char.sara import Hero
from maps.game_map import GameMap
from maps import map_data


class SaraAdventure:
    def __init__(self):
        pygame.init()

        self.screen_width = 640
        self.screen_height = 640
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Sara Adventure")

        # Load item images
        base_dir = os.path.dirname(os.path.abspath(__file__))
        trophy_path = os.path.join(base_dir, "assets", "items", "gold_trophy.png")
        self.item_images = {}
        if os.path.exists(trophy_path):
            self.item_images[map_data.TROPHY] = pygame.image.load(
                trophy_path
            ).convert_alpha()

        # Load sound effects if available
        self.sound_win = None
        self.sound_portal = None
        win_snd_path = os.path.join(base_dir, "assets", "sounds", "win.wav")
        port_snd_path = os.path.join(base_dir, "assets", "sounds", "portal.wav")
        if os.path.exists(win_snd_path):
            self.sound_win = pygame.mixer.Sound(win_snd_path)
            self.sound_win.set_volume(0.5)
        if os.path.exists(port_snd_path):
            self.sound_portal = pygame.mixer.Sound(port_snd_path)
            self.sound_portal.set_volume(0.5)

        # Create maps
        self.map_forest = GameMap.create_forest_map(base_dir, self.item_images)
        self.map_space = GameMap.create_space_map(base_dir, self.item_images)
        self.current_map = self.map_forest

        # Create Hero
        sara_img = os.path.join(base_dir, "assets", "sara", "sara_spritesheet.png")
        if not os.path.exists(sara_img):
            # Fallbacks just in case
            sara_img = os.path.join(base_dir, "assets", "sara", "sara-cal1.png")
            if not os.path.exists(sara_img):
                sara_img = os.path.join(base_dir, "char", "sara", "sara-cal1.png")

        self.hero = Hero(
            "Sara",
            sara_img,
            x=self.screen_width // 2,
            y=self.screen_height // 2,
            map_width=self.screen_width,
            map_height=self.screen_height,
        )

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 28, bold=True)

        self.state = "MENU"
        self.win_timer = 0

    def draw_text_centered(self, text, y, color=(255, 255, 255)):
        surface = self.font.render(text, True, color)
        rect = surface.get_rect(center=(self.screen_width // 2, y))
        # Drop shadow
        shadow = self.font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.screen_width // 2 + 2, y + 2))
        self.screen.blit(shadow, shadow_rect)
        self.screen.blit(surface, rect)

    def draw_hud(self):
        text = "Map: Forest" if self.current_map == self.map_forest else "Map: Space"
        surface = pygame.font.SysFont("Arial", 20).render(text, True, (255, 255, 255))
        shadow = pygame.font.SysFont("Arial", 20).render(text, True, (0, 0, 0))
        self.screen.blit(shadow, (12, 12))
        self.screen.blit(surface, (10, 10))

    def start(self):
        running = True
        while running:
            elapsed_time = self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.state == "MENU" and event.key == pygame.K_RETURN:
                        self.state = "PLAY"
                    elif self.state == "WIN" and event.key == pygame.K_RETURN:
                        # Reset game
                        self.state = "MENU"
                        self.current_map = self.map_forest
                        self.hero.rect.x = self.screen_width // 2
                        self.hero.rect.y = self.screen_height // 2
                        self.win_timer = 0
                        # Replenish trophy
                        self.map_space = GameMap.create_space_map(
                            os.path.dirname(os.path.abspath(__file__)), self.item_images
                        )

            if self.state == "MENU":
                self.screen.fill((20, 40, 60))
                self.draw_text_centered(
                    "SARA'S ADVENTURE", self.screen_height // 2 - 40, (255, 200, 50)
                )
                self.draw_text_centered(
                    "Press ENTER to Start", self.screen_height // 2 + 20
                )

            elif self.state == "PLAY":
                # Handle continuous input
                keys = pygame.key.get_pressed()
                moving = False
                if keys[pygame.K_LEFT]:
                    self.hero.left()
                    moving = True
                if keys[pygame.K_RIGHT]:
                    self.hero.right()
                    moving = True
                if keys[pygame.K_UP]:
                    self.hero.up()
                    moving = True
                if keys[pygame.K_DOWN]:
                    self.hero.down()
                    moving = True

                if moving:
                    self.hero.update(elapsed_time)

                # Interactions
                hero_center_x = self.hero.rect.centerx
                hero_center_y = self.hero.rect.centery

                if self.current_map == self.map_forest:
                    if self.current_map.has_portal(hero_center_x, hero_center_y):
                        if self.sound_portal:
                            self.sound_portal.play()
                        self.current_map = self.map_space
                        # Put hero at bottom of space map
                        self.hero.rect.x = self.screen_width // 2
                        self.hero.rect.y = self.screen_height - 64

                elif self.current_map == self.map_space:
                    if self.current_map.has_trophy(hero_center_x, hero_center_y):
                        if self.sound_win:
                            self.sound_win.play()
                        self.current_map.remove_item_at(hero_center_x, hero_center_y)
                        self.state = "WIN"

                # Render
                self.screen.fill((0, 0, 0))
                self.current_map.draw(self.screen)
                self.hero.draw(self.screen)
                self.draw_hud()

            elif self.state == "WIN":
                self.screen.fill((0, 0, 0))
                self.current_map.draw(self.screen)
                self.hero.draw(self.screen)

                # Dark overlay
                overlay = pygame.Surface((self.screen_width, self.screen_height))
                overlay.set_alpha(150)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 0))

                self.draw_text_centered(
                    "CONGRATULATIONS!", self.screen_height // 2 - 20, (50, 255, 50)
                )
                self.draw_text_centered(
                    "You collected the Trophy.", self.screen_height // 2 + 20
                )

                self.win_timer += elapsed_time
                if self.win_timer > 3000:
                    self.draw_text_centered(
                        "Press ENTER to Restart",
                        self.screen_height // 2 + 80,
                        (200, 200, 200),
                    )

            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = SaraAdventure()
    game.start()
