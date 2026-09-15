import pygame
import math
import random
from .constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GAME_WIDTH, LANE_WIDTH, NUM_LANES,
    CAMERA_PANEL_WIDTH, CAM_PREVIEW_W, CAM_PREVIEW_H, CAM_PREVIEW_X, CAM_PREVIEW_Y,
    COLOR_BG, COLOR_PANEL_BG, COLOR_LANE_1, COLOR_LANE_2, COLOR_LANE_LINE, COLOR_LANE_DASH,
    COLOR_WHITE, COLOR_GRAY, COLOR_DARK_GRAY, COLOR_SCORE, COLOR_GAMEOVER,
    COLOR_MENU_BG, COLOR_MENU_SEL, COLOR_ACTIVE, COLOR_INACTIVE,
    COLOR_GRAFFITI_1, COLOR_GRAFFITI_2, COLOR_GRAFFITI_3, COLOR_GRAFFITI_4,
)


class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font_big = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_med = pygame.font.SysFont("consolas", 24, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 18)
        self.font_xs = pygame.font.SysFont("consolas", 14)
        self.ground_offset = 0.0
        self._anim_tick = 0
        # Pre-generate graffiti splashes (static decorations on the "walls")
        self._graffiti = self._generate_graffiti()

    def _generate_graffiti(self):
        """Pre-generate random graffiti marks that scroll with the ground."""
        marks = []
        colors = [COLOR_GRAFFITI_1, COLOR_GRAFFITI_2, COLOR_GRAFFITI_3, COLOR_GRAFFITI_4]
        for _ in range(20):
            marks.append({
                "x": random.randint(5, GAME_WIDTH - 30),
                "y": random.randint(0, 2000),
                "color": random.choice(colors),
                "type": random.choice(["circle", "line", "star"]),
                "size": random.randint(4, 12),
            })
        return marks

    def draw_background(self, speed):
        self.screen.fill(COLOR_BG)
        self.ground_offset = (self.ground_offset + speed) % 2000
        self._anim_tick += 1

        # Lane fills
        for i in range(NUM_LANES):
            color = COLOR_LANE_1 if i % 2 == 0 else COLOR_LANE_2
            pygame.draw.rect(self.screen, color, (i * LANE_WIDTH, 0, LANE_WIDTH, SCREEN_HEIGHT))

        # Dashed lane dividers - bold colored
        dash_offset = self.ground_offset % 40
        for i in range(1, NUM_LANES):
            x = i * LANE_WIDTH
            y = -40 + int(dash_offset)
            while y < SCREEN_HEIGHT:
                pygame.draw.line(self.screen, COLOR_LANE_DASH, (x, y), (x, y + 20), 3)
                y += 40

        # Scrolling graffiti marks on the ground
        for mark in self._graffiti:
            my = (mark["y"] + int(self.ground_offset)) % 2000 - 500
            if 0 <= my < SCREEN_HEIGHT:
                mx = mark["x"]
                c = mark["color"]
                # Make graffiti semi-transparent by darkening
                dc = (c[0] // 3, c[1] // 3, c[2] // 3)
                if mark["type"] == "circle":
                    pygame.draw.circle(self.screen, dc, (mx, my), mark["size"], 2)
                elif mark["type"] == "line":
                    pygame.draw.line(self.screen, dc, (mx, my), (mx + mark["size"] * 3, my + 4), 2)
                elif mark["type"] == "star":
                    s = mark["size"]
                    pygame.draw.line(self.screen, dc, (mx - s, my), (mx + s, my), 2)
                    pygame.draw.line(self.screen, dc, (mx, my - s), (mx, my + s), 2)

        # Side panel background
        pygame.draw.rect(self.screen, COLOR_PANEL_BG,
                         (GAME_WIDTH, 0, CAMERA_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, COLOR_GRAFFITI_4, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)

    def draw_camera_feed(self, camera):
        """Draw the camera preview and command indicators in the side panel."""
        if camera is None:
            # No camera - draw placeholder
            pygame.draw.rect(self.screen, (40, 40, 55),
                             (CAM_PREVIEW_X, CAM_PREVIEW_Y, CAM_PREVIEW_W, CAM_PREVIEW_H),
                             border_radius=6)
            txt = self.font_sm.render("No Camera", True, COLOR_GRAY)
            self.screen.blit(txt, (
                CAM_PREVIEW_X + CAM_PREVIEW_W // 2 - txt.get_width() // 2,
                CAM_PREVIEW_Y + CAM_PREVIEW_H // 2 - txt.get_height() // 2,
            ))
            self._draw_command_indicators(set())
            return

        # Get camera frame as pygame surface
        surf = camera.get_pygame_surface(CAM_PREVIEW_W, CAM_PREVIEW_H)
        # Draw border
        pygame.draw.rect(self.screen, COLOR_GRAY,
                         (CAM_PREVIEW_X - 2, CAM_PREVIEW_Y - 2,
                          CAM_PREVIEW_W + 4, CAM_PREVIEW_H + 4),
                         border_radius=6)
        self.screen.blit(surf, (CAM_PREVIEW_X, CAM_PREVIEW_Y))

        # Get active actions and draw indicators
        active = camera.get_active_actions()
        self._draw_command_indicators(active)

    def _draw_command_indicators(self, active_actions):
        """Draw animated arrow indicators showing which commands are active."""
        panel_cx = GAME_WIDTH + CAMERA_PANEL_WIDTH // 2
        base_y = CAM_PREVIEW_Y + CAM_PREVIEW_H + 30

        label = self.font_sm.render("GESTURES", True, COLOR_GRAY)
        self.screen.blit(label, (panel_cx - label.get_width() // 2, base_y))

        # Arrow layout: UP top, LEFT/RIGHT middle, DOWN bottom
        cx = panel_cx
        arrow_y_up = base_y + 50
        arrow_y_mid = base_y + 110
        arrow_y_down = base_y + 170

        # Bounce animation amount for active arrows
        bounce = int(math.sin(self._anim_tick * 0.15) * 4)

        # UP arrow
        up_active = "UP" in active_actions
        self._draw_arrow_button(cx, arrow_y_up + (bounce if up_active else 0),
                                "UP", "Pinch Index", up_active)

        # LEFT arrow
        left_active = "LEFT" in active_actions
        self._draw_arrow_button(cx - 60, arrow_y_mid + (bounce if left_active else 0),
                                "LEFT", "Blink L", left_active)

        # RIGHT arrow
        right_active = "RIGHT" in active_actions
        self._draw_arrow_button(cx + 60, arrow_y_mid + (bounce if right_active else 0),
                                "RIGHT", "Blink R", right_active)

        # DOWN arrow
        down_active = "DOWN" in active_actions
        self._draw_arrow_button(cx, arrow_y_down + (bounce if down_active else 0),
                                "DOWN", "Pinch Mid", down_active)

        # Instructions at bottom of panel
        instr_y = arrow_y_down + 70
        try:
            from config import GestureConfig, GESTURE_LABELS, ACTION_LABELS
            cfg = GestureConfig()
            for gesture, action in cfg.mappings.items():
                if action != "NONE":
                    line = f"{GESTURE_LABELS[gesture]} = {ACTION_LABELS[action]}"
                    txt = self.font_xs.render(line, True, COLOR_DARK_GRAY)
                    self.screen.blit(txt, (GAME_WIDTH + 12, instr_y))
                    instr_y += 18
        except Exception:
            pass

    def _draw_arrow_button(self, cx, cy, direction, label, active):
        """Draw a single arrow indicator with label."""
        size = 22
        color = COLOR_ACTIVE if active else COLOR_INACTIVE
        glow_color = (0, 255, 120, 80) if active else None

        # Glow behind active arrows
        if active:
            glow = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 255, 120, 50), (size * 3 // 2, size * 3 // 2), size + 8)
            self.screen.blit(glow, (cx - size * 3 // 2, cy - size * 3 // 2))

        # Arrow triangles
        if direction == "UP":
            points = [(cx, cy - size), (cx - size, cy + size // 2), (cx + size, cy + size // 2)]
        elif direction == "DOWN":
            points = [(cx, cy + size), (cx - size, cy - size // 2), (cx + size, cy - size // 2)]
        elif direction == "LEFT":
            points = [(cx - size, cy), (cx + size // 2, cy - size), (cx + size // 2, cy + size)]
        elif direction == "RIGHT":
            points = [(cx + size, cy), (cx - size // 2, cy - size), (cx - size // 2, cy + size)]
        else:
            return

        pygame.draw.polygon(self.screen, color, points)
        if active:
            pygame.draw.polygon(self.screen, COLOR_WHITE, points, 2)

        # Label below/beside the arrow
        txt = self.font_xs.render(label, True, color)
        if direction in ("UP", "DOWN"):
            self.screen.blit(txt, (cx - txt.get_width() // 2, cy + size + 8))
        elif direction == "LEFT":
            self.screen.blit(txt, (cx - txt.get_width() // 2, cy + size + 8))
        elif direction == "RIGHT":
            self.screen.blit(txt, (cx - txt.get_width() // 2, cy + size + 8))

    def draw_hud(self, score, speed):
        score_surf = self.font_med.render(f"Score: {score}", True, COLOR_SCORE)
        self.screen.blit(score_surf, (10, 10))

        speed_surf = self.font_sm.render(f"Speed: {speed:.1f}", True, COLOR_GRAY)
        self.screen.blit(speed_surf, (10, 40))

    def draw_game_over(self, score):
        overlay = pygame.Surface((GAME_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        cx = GAME_WIDTH // 2
        title = self.font_big.render("GAME OVER", True, COLOR_GAMEOVER)
        self.screen.blit(title, (cx - title.get_width() // 2, SCREEN_HEIGHT // 2 - 80))

        sc = self.font_med.render(f"Score: {score}", True, COLOR_WHITE)
        self.screen.blit(sc, (cx - sc.get_width() // 2, SCREEN_HEIGHT // 2 - 20))

        r1 = self.font_sm.render("ENTER to restart", True, COLOR_GRAY)
        r2 = self.font_sm.render("ESC to quit", True, COLOR_GRAY)
        self.screen.blit(r1, (cx - r1.get_width() // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(r2, (cx - r2.get_width() // 2, SCREEN_HEIGHT // 2 + 55))

    def draw_title_screen(self, camera=None):
        self.screen.fill(COLOR_MENU_BG)
        self._anim_tick += 1

        cx = GAME_WIDTH // 2
        title = self.font_big.render("SUBWAY RUNNER", True, COLOR_MENU_SEL)
        self.screen.blit(title, (cx - title.get_width() // 2, 120))

        controls = [
            "Controls:",
            "",
            "Arrow keys / WASD",
            "  or Camera gestures",
            "",
            "UP    - Jump",
            "DOWN  - Slide",
            "LEFT  - Move left",
            "RIGHT - Move right",
            "",
            "Press ENTER to start",
            "Press ESC to quit",
        ]
        y = 220
        for line in controls:
            color = COLOR_WHITE if line == "Controls:" else COLOR_GRAY
            surf = self.font_sm.render(line, True, color)
            self.screen.blit(surf, (cx - surf.get_width() // 2, y))
            y += 24

        # Draw camera panel on title screen too
        pygame.draw.rect(self.screen, COLOR_PANEL_BG,
                         (GAME_WIDTH, 0, CAMERA_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(self.screen, COLOR_GRAY, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)
        self.draw_camera_feed(camera)
