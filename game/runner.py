import pygame
import sys
from .constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_Y
from .player import Player
from .obstacles import ObstacleManager
from .renderer import Renderer


class Game:
    def __init__(self, use_camera=False):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Subway Runner")
        self.clock = pygame.time.Clock()
        self.renderer = Renderer(self.screen)

        self.camera = None
        if use_camera:
            from camera_controller import CameraController
            self.camera = CameraController(cooldown_ms=400, show_preview=False)
            self.camera.start()

    def run(self):
        while True:
            result = self._title_screen()
            if result == "quit":
                break
            result = self._game_loop()
            if result == "quit":
                break
        self._cleanup()

    def _title_screen(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "play"
                    if event.key == pygame.K_ESCAPE:
                        return "quit"

            if self.camera:
                for action in self.camera.get_actions():
                    if action == "UP":
                        return "play"

            self.renderer.draw_title_screen(camera=self.camera)
            pygame.display.flip()
            self.clock.tick(FPS)

    def _game_loop(self):
        player = Player()
        obstacles = ObstacleManager()
        game_over = False

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key == pygame.K_RETURN:
                            return "restart"
                        if event.key == pygame.K_ESCAPE:
                            return "quit"
                    else:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            player.jump()
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            player.slide()
                        elif event.key in (pygame.K_LEFT, pygame.K_a):
                            player.move_left()
                        elif event.key in (pygame.K_RIGHT, pygame.K_d):
                            player.move_right()
                        elif event.key == pygame.K_ESCAPE:
                            return "quit"

            # Camera actions
            if self.camera and not game_over:
                for action in self.camera.get_actions():
                    if action == "UP":
                        player.jump()
                    elif action == "DOWN":
                        player.slide()
                    elif action == "LEFT":
                        player.move_left()
                    elif action == "RIGHT":
                        player.move_right()

            if not game_over:
                player.update()
                obstacles.update()

                jump_height = player.y - PLAYER_Y
                if obstacles.check_collision(
                    player.get_rect(), player.is_sliding, player.is_jumping, jump_height
                ):
                    player.alive = False
                    game_over = True

            # Draw
            self.renderer.draw_background(obstacles.speed)
            for obs in obstacles.obstacles:
                obs.draw(self.screen)
            player.draw(self.screen)
            self.renderer.draw_hud(obstacles.score, obstacles.speed)

            # Camera feed + gesture indicators (always visible in side panel)
            self.renderer.draw_camera_feed(self.camera)

            if game_over:
                self.renderer.draw_game_over(obstacles.score)
                if self.camera:
                    for action in self.camera.get_actions():
                        if action == "UP":
                            return "restart"

            pygame.display.flip()
            self.clock.tick(FPS)

    def _cleanup(self):
        if self.camera:
            self.camera.stop()
        pygame.quit()
