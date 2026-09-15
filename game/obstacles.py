import pygame
import random
from .constants import (
    SCREEN_HEIGHT, LANE_WIDTH, LANE_CENTERS, PLAYER_WIDTH,
    INITIAL_SPEED, SPEED_INCREMENT, MIN_SPAWN_GAP,
    COLOR_BARRIER, COLOR_OVERHEAD, COLOR_TRAIN, COLOR_TRAIN_STRIPE,
    COLOR_TRAIN_WINDOW, COLOR_GRAFFITI_1, COLOR_GRAFFITI_2, COLOR_GRAFFITI_3,
)

# Obstacle types
BARRIER = "barrier"      # ground-level block, jump to avoid
OVERHEAD = "overhead"    # floating bar, slide to avoid
TRAIN = "train"          # tall block filling a lane, dodge sideways


class Obstacle:
    def __init__(self, lane, obs_type, speed):
        self.lane = lane
        self.type = obs_type
        self.x = LANE_CENTERS[lane]
        self.speed = speed

        if obs_type == BARRIER:
            self.width = 50
            self.height = 40
            self.y = -self.height
        elif obs_type == OVERHEAD:
            self.width = LANE_WIDTH - 10
            self.height = 25
            self.y = -self.height
        else:  # TRAIN
            self.width = LANE_WIDTH - 10
            self.height = 140
            self.y = -self.height

    def update(self, speed):
        self.speed = speed
        self.y += speed

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 20

    def get_rect(self):
        return pygame.Rect(
            self.x - self.width // 2,
            int(self.y),
            self.width,
            self.height,
        )

    def draw(self, surface):
        rect = self.get_rect()
        if self.type == BARRIER:
            # Road barrier - bold graffiti red with warning stripes
            pygame.draw.rect(surface, COLOR_BARRIER, rect, border_radius=5)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=5)
            # Diagonal warning stripes
            for i in range(0, rect.width + rect.height, 12):
                x1 = rect.left + i
                y1 = rect.top
                x2 = rect.left + i - rect.height
                y2 = rect.bottom
                pygame.draw.line(surface, (255, 130, 150),
                                 (max(x1, rect.left), max(y1, rect.top)),
                                 (max(x2, rect.left), min(y2, rect.bottom)), 2)
        elif self.type == OVERHEAD:
            # Overhead sign - yellow with graffiti tag
            pole_x1 = rect.left + 6
            pole_x2 = rect.right - 6
            pygame.draw.line(surface, (180, 140, 0), (pole_x1, rect.bottom), (pole_x1, rect.bottom + 55), 4)
            pygame.draw.line(surface, (180, 140, 0), (pole_x2, rect.bottom), (pole_x2, rect.bottom + 55), 4)
            pygame.draw.rect(surface, COLOR_OVERHEAD, rect, border_radius=4)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=4)
            # Graffiti squiggle on the sign
            mid = rect.centery
            pygame.draw.line(surface, COLOR_GRAFFITI_1,
                             (rect.left + 8, mid), (rect.right - 8, mid - 3), 3)
        else:  # TRAIN
            # Subway train car - purple with graffiti
            pygame.draw.rect(surface, COLOR_TRAIN, rect, border_radius=8)
            # Graffiti stripe
            stripe_y = rect.centery
            pygame.draw.rect(surface, COLOR_TRAIN_STRIPE,
                             (rect.left + 3, stripe_y - 6, rect.width - 6, 12),
                             border_radius=3)
            # Roof line
            pygame.draw.rect(surface, (100, 40, 180),
                             (rect.left + 2, rect.top, rect.width - 4, 8),
                             border_radius=4)
            # Windows
            for wy in range(rect.top + 18, rect.bottom - 25, 28):
                pygame.draw.rect(surface, COLOR_TRAIN_WINDOW,
                                 (rect.left + 8, wy, 16, 14), border_radius=3)
                pygame.draw.rect(surface, COLOR_TRAIN_WINDOW,
                                 (rect.right - 24, wy, 16, 14), border_radius=3)
            # Graffiti tag on the train
            tag_y = rect.bottom - 30
            pygame.draw.line(surface, COLOR_GRAFFITI_2,
                             (rect.left + 6, tag_y), (rect.right - 6, tag_y - 5), 3)
            pygame.draw.line(surface, COLOR_GRAFFITI_3,
                             (rect.left + 10, tag_y + 6), (rect.right - 10, tag_y + 2), 2)
            # Outline
            pygame.draw.rect(surface, (200, 120, 255), rect, 2, border_radius=8)


class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.speed = INITIAL_SPEED
        self.frames_since_spawn = 0
        self.score = 0
        self._frame_count = 0

    def update(self):
        self._frame_count += 1
        self.speed = INITIAL_SPEED + self._frame_count * SPEED_INCREMENT
        self.score = self._frame_count
        self.frames_since_spawn += 1

        for obs in self.obstacles:
            obs.update(self.speed)

        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        if self.frames_since_spawn >= max(MIN_SPAWN_GAP, int(70 - self.speed * 3)):
            self._spawn()
            self.frames_since_spawn = 0

    def _spawn(self):
        # Pick 1 or 2 lanes to block, always leave at least 1 lane open
        num = 1
        if self.speed > 7 and random.random() < 0.35:
            num = 2

        lanes = random.sample(range(3), num)

        for lane in lanes:
            # Choose type weighted by difficulty
            if self.speed < 6.5:
                obs_type = random.choice([BARRIER, BARRIER, OVERHEAD])
            else:
                obs_type = random.choice([BARRIER, OVERHEAD, TRAIN])
            self.obstacles.append(Obstacle(lane, obs_type, self.speed))

    def check_collision(self, player_rect, is_sliding, is_jumping, jump_height):
        for obs in self.obstacles:
            obs_rect = obs.get_rect()
            if not player_rect.colliderect(obs_rect):
                continue

            if obs.type == BARRIER:
                # Can jump over barriers
                if is_jumping and jump_height < -30:
                    continue
                return True
            elif obs.type == OVERHEAD:
                # Can slide under overheads
                if is_sliding:
                    continue
                return True
            else:  # TRAIN
                # Must dodge sideways - any overlap is a hit
                return True

        return False
