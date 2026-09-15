import pygame
from .constants import (
    LANE_CENTERS, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_Y,
    JUMP_VELOCITY, GRAVITY, SLIDE_DURATION_FRAMES, SLIDE_HEIGHT,
    LANE_LERP, COLOR_PLAYER, COLOR_PLAYER_HEAD, COLOR_PLAYER_SLIDE,
    COLOR_PLAYER_OUTLINE, COLOR_GRAFFITI_1,
)


class Player:
    def __init__(self):
        self.lane = 1
        self.x = float(LANE_CENTERS[self.lane])
        self.y = float(PLAYER_Y)
        self.vy = 0.0
        self.is_jumping = False
        self.is_sliding = False
        self.slide_timer = 0
        self.alive = True
        self._frame = 0

    def jump(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_jumping = True
            self.vy = JUMP_VELOCITY

    def slide(self):
        if not self.is_jumping and not self.is_sliding:
            self.is_sliding = True
            self.slide_timer = SLIDE_DURATION_FRAMES

    def move_left(self):
        if self.lane > 0:
            self.lane -= 1

    def move_right(self):
        if self.lane < 2:
            self.lane += 1

    def update(self):
        self._frame += 1
        # Smooth lane transition
        target_x = float(LANE_CENTERS[self.lane])
        self.x += (target_x - self.x) * LANE_LERP

        # Jumping physics
        if self.is_jumping:
            self.y += self.vy
            self.vy += GRAVITY
            if self.y >= PLAYER_Y:
                self.y = PLAYER_Y
                self.vy = 0
                self.is_jumping = False

        # Slide timer
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False

    def get_rect(self):
        cx = int(self.x)
        if self.is_sliding:
            return pygame.Rect(
                cx - PLAYER_WIDTH // 2,
                int(self.y) + PLAYER_HEIGHT - SLIDE_HEIGHT,
                PLAYER_WIDTH,
                SLIDE_HEIGHT,
            )
        return pygame.Rect(
            cx - PLAYER_WIDTH // 2,
            int(self.y),
            PLAYER_WIDTH,
            PLAYER_HEIGHT,
        )

    def draw(self, surface):
        cx = int(self.x)
        y = int(self.y)

        if self.is_sliding:
            # Flat sliding body - graffiti style
            rect = pygame.Rect(
                cx - PLAYER_WIDTH // 2 - 3,
                y + PLAYER_HEIGHT - SLIDE_HEIGHT,
                PLAYER_WIDTH + 6,
                SLIDE_HEIGHT,
            )
            pygame.draw.rect(surface, COLOR_PLAYER_SLIDE, rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_PLAYER_OUTLINE, rect, 2, border_radius=8)
            # Speed lines
            for i in range(3):
                ly = rect.y + 5 + i * 8
                pygame.draw.line(surface, COLOR_PLAYER_OUTLINE,
                                 (rect.x - 15 - i * 4, ly), (rect.x - 4, ly), 2)
        else:
            # ── Subway surfer character ──
            leg_offset = 5 if (self._frame // 6) % 2 == 0 else 0

            # Legs (animated running)
            if not self.is_jumping:
                pygame.draw.rect(surface, COLOR_PLAYER,
                                 (cx - 12, y + PLAYER_HEIGHT - 5, 10, 15 + leg_offset),
                                 border_radius=3)
                pygame.draw.rect(surface, COLOR_PLAYER,
                                 (cx + 2, y + PLAYER_HEIGHT - 5, 10, 15 + (5 - leg_offset)),
                                 border_radius=3)
            else:
                # Tucked legs while jumping
                pygame.draw.rect(surface, COLOR_PLAYER,
                                 (cx - 12, y + PLAYER_HEIGHT - 5, 10, 10),
                                 border_radius=3)
                pygame.draw.rect(surface, COLOR_PLAYER,
                                 (cx + 2, y + PLAYER_HEIGHT - 5, 10, 10),
                                 border_radius=3)

            # Body
            body = pygame.Rect(cx - PLAYER_WIDTH // 2, y + 22, PLAYER_WIDTH, PLAYER_HEIGHT - 22)
            pygame.draw.rect(surface, COLOR_PLAYER, body, border_radius=10)
            pygame.draw.rect(surface, COLOR_PLAYER_OUTLINE, body, 2, border_radius=10)

            # Hoodie/shirt stripe
            pygame.draw.rect(surface, COLOR_GRAFFITI_1,
                             (cx - PLAYER_WIDTH // 2 + 4, y + 38, PLAYER_WIDTH - 8, 8),
                             border_radius=3)

            # Head
            pygame.draw.circle(surface, COLOR_PLAYER_HEAD, (cx, y + 14), 16)
            pygame.draw.circle(surface, COLOR_PLAYER_OUTLINE, (cx, y + 14), 16, 2)

            # Cap/beanie
            pygame.draw.rect(surface, COLOR_GRAFFITI_1,
                             (cx - 14, y, 28, 12), border_radius=5)
            pygame.draw.rect(surface, (255, 120, 200),
                             (cx - 16, y + 8, 32, 5), border_radius=2)

            # Eyes
            pygame.draw.circle(surface, (255, 255, 255), (cx - 5, y + 12), 4)
            pygame.draw.circle(surface, (255, 255, 255), (cx + 5, y + 12), 4)
            pygame.draw.circle(surface, (20, 20, 20), (cx - 4, y + 12), 2)
            pygame.draw.circle(surface, (20, 20, 20), (cx + 6, y + 12), 2)

            # Mouth - grin
            pygame.draw.arc(surface, (20, 20, 20),
                            (cx - 6, y + 14, 12, 8), 3.14, 6.28, 2)
