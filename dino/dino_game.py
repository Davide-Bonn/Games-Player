import pygame
import random
import math
import sys
import os

# ── Chrome Dino style constants ──
SCREEN_W = 750
GAME_H = 300
CAM_PANEL_H = 200
SCREEN_H = GAME_H + CAM_PANEL_H
FPS = 60
GROUND_Y = GAME_H - 50

# Chrome Dino palette - monochrome
BG = (247, 247, 247)
DINO_COLOR = (83, 83, 83)
CACTUS_COLOR = (83, 83, 83)
BIRD_COLOR = (83, 83, 83)
GROUND_COLOR = (83, 83, 83)
CLOUD_COLOR = (200, 200, 200)
SCORE_COLOR = (83, 83, 83)
GAMEOVER_COLOR = (83, 83, 83)
WHITE = (255, 255, 255)
# Camera panel (dark)
PANEL_BG = (22, 22, 30)
PANEL_TEXT = (160, 160, 170)
PANEL_DIM = (80, 80, 90)
CAM_BORDER = (100, 100, 120)
ACTIVE_COLOR = (0, 255, 120)
INACTIVE_COLOR = (60, 60, 80)


class Dino:
    def __init__(self):
        self.x = 60
        self.y = GROUND_Y
        self.w = 44
        self.h = 47
        self.vy = 0
        self.jumping = False
        self.ducking = False
        self.duck_h = 26
        self.duck_w = 59
        self.run_frame = 0

    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.ducking = False
            self.vy = -13

    def duck(self, active):
        if not self.jumping:
            self.ducking = active

    def update(self):
        if self.jumping:
            self.y += self.vy
            self.vy += 0.6
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.jumping = False
                self.vy = 0
        self.run_frame += 1

    def get_rect(self):
        if self.ducking:
            return pygame.Rect(self.x, self.y + self.h - self.duck_h, self.duck_w, self.duck_h)
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf):
        c = DINO_COLOR
        if self.ducking:
            bx, by = self.x, self.y + self.h - self.duck_h
            # Flat body
            pygame.draw.rect(surf, c, (bx, by + 2, self.duck_w - 10, self.duck_h - 4))
            # Head
            pygame.draw.rect(surf, c, (bx + self.duck_w - 20, by, 20, 16))
            # Eye
            pygame.draw.rect(surf, BG, (bx + self.duck_w - 8, by + 4, 4, 4))
            # Legs
            leg = 4 if (self.run_frame // 5) % 2 == 0 else 0
            pygame.draw.rect(surf, c, (bx + 6, by + self.duck_h - 2, 6, 8 + leg))
            pygame.draw.rect(surf, c, (bx + 20, by + self.duck_h - 2, 6, 8 + (4 - leg)))
        else:
            bx, by = self.x, int(self.y)
            # Body
            pygame.draw.rect(surf, c, (bx + 4, by + 12, 30, 28))
            # Neck
            pygame.draw.rect(surf, c, (bx + 20, by + 4, 14, 14))
            # Head
            pygame.draw.rect(surf, c, (bx + 14, by, 30, 18))
            # Eye (white square cutout)
            pygame.draw.rect(surf, BG, (bx + 36, by + 4, 4, 5))
            # Mouth slit
            pygame.draw.rect(surf, BG, (bx + 30, by + 14, 14, 2))
            # Tail
            pygame.draw.rect(surf, c, (bx, by + 14, 8, 6))
            pygame.draw.rect(surf, c, (bx - 4, by + 12, 6, 4))
            # Arms
            pygame.draw.rect(surf, c, (bx + 26, by + 28, 10, 4))
            pygame.draw.rect(surf, c, (bx + 34, by + 30, 4, 6))
            # Legs
            if self.jumping:
                # Legs straight
                pygame.draw.rect(surf, c, (bx + 10, by + self.h, 6, 10))
                pygame.draw.rect(surf, c, (bx + 22, by + self.h, 6, 10))
            else:
                leg = (self.run_frame // 5) % 2
                if leg == 0:
                    pygame.draw.rect(surf, c, (bx + 10, by + self.h, 6, 12))
                    pygame.draw.rect(surf, c, (bx + 16, by + self.h + 10, 6, 2))
                    pygame.draw.rect(surf, c, (bx + 22, by + self.h, 6, 6))
                else:
                    pygame.draw.rect(surf, c, (bx + 10, by + self.h, 6, 6))
                    pygame.draw.rect(surf, c, (bx + 22, by + self.h, 6, 12))
                    pygame.draw.rect(surf, c, (bx + 28, by + self.h + 10, 6, 2))


class Cactus:
    SHAPES = ["small", "medium", "large", "double"]

    def __init__(self, x, speed):
        self.shape = random.choice(self.SHAPES)
        self.x = x
        self.speed = speed

        if self.shape == "small":
            self.w, self.h = 14, 34
        elif self.shape == "medium":
            self.w, self.h = 18, 42
        elif self.shape == "large":
            self.w, self.h = 24, 50
        else:  # double
            self.w, self.h = 36, 38

        self.y = GROUND_Y + 47 - self.h  # sit on ground line

    def update(self, speed):
        self.speed = speed
        self.x -= speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf):
        c = CACTUS_COLOR
        x, y, w, h = self.x, self.y, self.w, self.h

        if self.shape == "small":
            # Single thin cactus
            pygame.draw.rect(surf, c, (x + 4, y, 6, h))
            # Arms
            pygame.draw.rect(surf, c, (x, y + 10, 6, 4))
            pygame.draw.rect(surf, c, (x, y + 6, 4, 8))
            pygame.draw.rect(surf, c, (x + 10, y + 16, 4, 4))
            pygame.draw.rect(surf, c, (x + 10, y + 14, 4, 6))
        elif self.shape == "medium":
            pygame.draw.rect(surf, c, (x + 5, y, 8, h))
            pygame.draw.rect(surf, c, (x, y + 12, 7, 4))
            pygame.draw.rect(surf, c, (x, y + 8, 4, 8))
            pygame.draw.rect(surf, c, (x + 12, y + 20, 6, 4))
            pygame.draw.rect(surf, c, (x + 14, y + 16, 4, 8))
        elif self.shape == "large":
            pygame.draw.rect(surf, c, (x + 7, y, 10, h))
            pygame.draw.rect(surf, c, (x, y + 14, 9, 5))
            pygame.draw.rect(surf, c, (x, y + 8, 5, 12))
            pygame.draw.rect(surf, c, (x + 16, y + 22, 8, 5))
            pygame.draw.rect(surf, c, (x + 19, y + 16, 5, 12))
        else:  # double
            pygame.draw.rect(surf, c, (x + 4, y + 4, 6, h - 4))
            pygame.draw.rect(surf, c, (x, y + 14, 4, 6))
            pygame.draw.rect(surf, c, (x + 22, y, 8, h))
            pygame.draw.rect(surf, c, (x + 30, y + 10, 6, 4))
            pygame.draw.rect(surf, c, (x + 32, y + 6, 4, 10))
            pygame.draw.rect(surf, c, (x + 10, y + h - 6, 12, 6))

    def is_off(self):
        return self.x + self.w < -10


class Bird:
    def __init__(self, x, speed):
        self.x = x
        self.y = GROUND_Y - random.choice([24, 50, 76])
        self.w = 42
        self.h = 20
        self.speed = speed
        self.frame = 0

    def update(self, speed):
        self.speed = speed
        self.x -= speed + 1.5
        self.frame += 1

    def get_rect(self):
        return pygame.Rect(self.x + 4, self.y + 4, self.w - 8, self.h - 8)

    def draw(self, surf):
        c = BIRD_COLOR
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        # Body
        pygame.draw.rect(surf, c, (self.x + 6, cy - 3, self.w - 12, 6))
        # Beak
        pygame.draw.rect(surf, c, (self.x + self.w - 6, cy - 2, 8, 3))
        # Wing flap
        wing_up = (self.frame // 8) % 2 == 0
        if wing_up:
            pygame.draw.rect(surf, c, (cx - 6, self.y, 12, 4))
            pygame.draw.rect(surf, c, (cx - 4, self.y + 4, 8, 4))
        else:
            pygame.draw.rect(surf, c, (cx - 6, cy + 3, 12, 4))
            pygame.draw.rect(surf, c, (cx - 4, cy + 7, 8, 4))
        # Eye
        pygame.draw.rect(surf, BG, (self.x + self.w - 14, cy - 4, 3, 3))

    def is_off(self):
        return self.x + self.w < -10


class Cloud:
    def __init__(self, x=None):
        self.x = x if x is not None else random.randint(SCREEN_W, SCREEN_W + 400)
        self.y = random.randint(30, GROUND_Y - 80)
        self.w = random.randint(46, 80)
        self.speed = random.uniform(0.3, 1.0)

    def update(self):
        self.x -= self.speed

    def draw(self, surf):
        c = CLOUD_COLOR
        # Simple blocky cloud like Chrome
        h = 14
        pygame.draw.rect(surf, c, (self.x + 10, self.y, self.w - 20, h))
        pygame.draw.rect(surf, c, (self.x, self.y + 4, self.w, h - 4))
        pygame.draw.rect(surf, c, (self.x + 5, self.y + h - 2, self.w - 10, 4))

    def is_off(self):
        return self.x + self.w < -10


class DinoGameLocal:
    def __init__(self, use_camera=False):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Dino Runner")
        self.clock = pygame.time.Clock()
        # Chrome uses a simple monospace font
        self.font_big = pygame.font.SysFont("consolas", 28, bold=True)
        self.font_med = pygame.font.SysFont("consolas", 20, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 16)
        self.font_xs = pygame.font.SysFont("consolas", 13)

        self.camera = None
        if use_camera:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from camera_controller import CameraController
            self.camera = CameraController(cooldown_ms=400, show_preview=False)
            self.camera.start()

        self._anim_tick = 0
        self.hi_score = 0

    def run(self):
        while True:
            result = self._title()
            if result == "quit":
                break
            result = self._play()
            if result == "quit":
                break
        self._cleanup()

    def _title(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_UP):
                        return "play"
                    if event.key == pygame.K_ESCAPE:
                        return "quit"
            if self.camera:
                for a in self.camera.get_actions():
                    if a == "UP":
                        return "play"

            self._anim_tick += 1
            self.screen.fill(BG)

            # Ground line
            pygame.draw.line(self.screen, GROUND_COLOR, (0, GROUND_Y + 47), (SCREEN_W, GROUND_Y + 47), 1)

            cx = SCREEN_W // 2

            # Static dino
            preview = Dino()
            preview.x = cx - 22
            preview.y = GROUND_Y
            preview.run_frame = 0
            preview.draw(self.screen)

            # "No internet" style text
            t = self.font_med.render("Press SPACE or UP to start", True, SCORE_COLOR)
            self.screen.blit(t, (cx - t.get_width() // 2, GROUND_Y - 80))

            if self.hi_score > 0:
                hi = self.font_sm.render(f"HI {self.hi_score:05d}", True, (180, 180, 180))
                self.screen.blit(hi, (SCREEN_W - hi.get_width() - 20, 15))

            self._draw_cam_panel()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _play(self):
        dino = Dino()
        obstacles = []
        clouds = [Cloud(x=random.randint(0, SCREEN_W)) for _ in range(3)]
        speed = 6.0
        score = 0
        spawn_timer = 0
        game_over = False
        ground_offset = 0.0

        # Ground bumps (random small marks like Chrome)
        ground_bumps = [(random.randint(0, SCREEN_W), random.choice([1, 2, 3])) for _ in range(30)]

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if game_over:
                        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_UP):
                            return "restart"
                        if event.key == pygame.K_ESCAPE:
                            return "quit"
                    else:
                        if event.key in (pygame.K_UP, pygame.K_SPACE, pygame.K_w):
                            dino.jump()
                        if event.key in (pygame.K_DOWN, pygame.K_s):
                            dino.duck(True)
                        if event.key == pygame.K_ESCAPE:
                            return "quit"
                if event.type == pygame.KEYUP:
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        dino.duck(False)

            if self.camera and not game_over:
                for a in self.camera.get_actions():
                    if a == "UP":
                        dino.jump()
                    elif a == "DOWN":
                        dino.duck(True)

            if not game_over:
                self._anim_tick += 1
                score += 1
                speed = 6.0 + score * 0.002
                ground_offset = (ground_offset + speed) % SCREEN_W

                dino.update()

                spawn_timer += 1
                gap = max(35, int(80 - speed * 2))
                if spawn_timer >= gap:
                    spawn_timer = 0
                    if random.random() < 0.25 and speed > 8:
                        obstacles.append(Bird(SCREEN_W + 20, speed))
                    else:
                        obstacles.append(Cactus(SCREEN_W + 20, speed))

                for obs in obstacles:
                    obs.update(speed)
                obstacles = [o for o in obstacles if not o.is_off()]

                for cloud in clouds:
                    cloud.update()
                clouds = [c for c in clouds if not c.is_off()]
                if random.random() < 0.008:
                    clouds.append(Cloud())

                # Collision
                dr = dino.get_rect()
                for obs in obstacles:
                    if dr.colliderect(obs.get_rect()):
                        if isinstance(obs, Bird) and dino.ducking and obs.y > GROUND_Y - 40:
                            continue
                        game_over = True
                        self.hi_score = max(self.hi_score, score)
                        break

            # ── Draw ──
            self.screen.fill(BG)

            # Clouds
            for cloud in clouds:
                cloud.draw(self.screen)

            # Ground line
            gy = GROUND_Y + 47
            pygame.draw.line(self.screen, GROUND_COLOR, (0, gy), (SCREEN_W, gy), 1)

            # Ground bumps (scrolling)
            for bx, bh in ground_bumps:
                rx = (bx - ground_offset) % SCREEN_W
                pygame.draw.rect(self.screen, GROUND_COLOR, (int(rx), gy + 2, bh, 1))

            # Obstacles
            for obs in obstacles:
                obs.draw(self.screen)

            # Dino
            dino.draw(self.screen)

            # Score (Chrome style: right-aligned, 5 digits)
            score_txt = self.font_sm.render(f"{score:05d}", True, SCORE_COLOR)
            self.screen.blit(score_txt, (SCREEN_W - score_txt.get_width() - 20, 15))

            if self.hi_score > 0:
                hi = self.font_sm.render(f"HI {self.hi_score:05d}", True, (180, 180, 180))
                self.screen.blit(hi, (SCREEN_W - score_txt.get_width() - hi.get_width() - 40, 15))

            # Game over
            if game_over:
                # "GAME OVER" text + restart icon (like Chrome)
                go = self.font_big.render("G A M E  O V E R", True, GAMEOVER_COLOR)
                self.screen.blit(go, (SCREEN_W // 2 - go.get_width() // 2, GAME_H // 2 - 40))

                # Restart arrow icon (circular)
                rcx = SCREEN_W // 2
                rcy = GAME_H // 2 + 10
                pygame.draw.circle(self.screen, DINO_COLOR, (rcx, rcy), 16, 2)
                # Arrow head on the circle
                pygame.draw.polygon(self.screen, DINO_COLOR, [
                    (rcx + 4, rcy - 16), (rcx + 12, rcy - 10), (rcx + 4, rcy - 10)
                ])
                # "Press SPACE" hint
                hint = self.font_xs.render("SPACE to restart  |  ESC to quit", True, (180, 180, 180))
                self.screen.blit(hint, (SCREEN_W // 2 - hint.get_width() // 2, GAME_H // 2 + 38))

            # Camera panel
            self._draw_cam_panel()
            pygame.display.flip()
            self.clock.tick(FPS)

    def _draw_cam_panel(self):
        panel_y = GAME_H
        pygame.draw.rect(self.screen, PANEL_BG, (0, panel_y, SCREEN_W, CAM_PANEL_H))
        pygame.draw.line(self.screen, (60, 60, 70), (0, panel_y), (SCREEN_W, panel_y), 1)

        cam_w, cam_h = 240, 170
        cam_x, cam_y = 15, panel_y + 15

        active = set()
        if self.camera:
            active = self.camera.get_active_actions()
            surf = self.camera.get_pygame_surface(cam_w, cam_h)
            pygame.draw.rect(self.screen, CAM_BORDER,
                             (cam_x - 2, cam_y - 2, cam_w + 4, cam_h + 4), border_radius=6)
            self.screen.blit(surf, (cam_x, cam_y))
        else:
            pygame.draw.rect(self.screen, (35, 35, 45),
                             (cam_x, cam_y, cam_w, cam_h), border_radius=6)
            txt = self.font_sm.render("No Camera", True, PANEL_DIM)
            self.screen.blit(txt, (cam_x + cam_w // 2 - txt.get_width() // 2,
                                   cam_y + cam_h // 2 - txt.get_height() // 2))

        # Gesture indicators
        ind_x = cam_x + cam_w + 30
        ind_y = panel_y + 20

        label = self.font_sm.render("GESTURES", True, PANEL_DIM)
        self.screen.blit(label, (ind_x + 50 - label.get_width() // 2, ind_y))

        bounce = int(math.sin(self._anim_tick * 0.15) * 3)

        up_on = "UP" in active
        self._draw_arrow(ind_x + 50, ind_y + 42 + (bounce if up_on else 0), "UP", "Jump", up_on)
        dn_on = "DOWN" in active
        self._draw_arrow(ind_x + 50, ind_y + 105 + (bounce if dn_on else 0), "DOWN", "Duck", dn_on)

        # Config-based instructions
        try:
            from config import GestureConfig, GESTURE_LABELS, ACTION_LABELS
            cfg = GestureConfig()
            instr_x = ind_x + 130
            iy = ind_y + 20
            for gesture, action in cfg.mappings.items():
                if action != "NONE":
                    line = f"{GESTURE_LABELS[gesture]}"
                    t = self.font_xs.render(line, True, PANEL_DIM)
                    self.screen.blit(t, (instr_x, iy))
                    a = self.font_xs.render(f"= {ACTION_LABELS[action]}", True, PANEL_TEXT)
                    self.screen.blit(a, (instr_x, iy + 14))
                    iy += 34
                    if iy > panel_y + CAM_PANEL_H - 20:
                        break
        except Exception:
            pass

    def _draw_arrow(self, cx, cy, direction, label, active):
        size = 16
        color = ACTIVE_COLOR if active else INACTIVE_COLOR

        if active:
            glow = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            pygame.draw.circle(glow, (0, 255, 120, 50), (size * 3 // 2, size * 3 // 2), size + 5)
            self.screen.blit(glow, (cx - size * 3 // 2, cy - size * 3 // 2))

        if direction == "UP":
            pts = [(cx, cy - size), (cx - size, cy + size // 2), (cx + size, cy + size // 2)]
        else:
            pts = [(cx, cy + size), (cx - size, cy - size // 2), (cx + size, cy - size // 2)]

        pygame.draw.polygon(self.screen, color, pts)
        if active:
            pygame.draw.polygon(self.screen, WHITE, pts, 2)

        if label:
            t = self.font_xs.render(label, True, color)
            self.screen.blit(t, (cx - t.get_width() // 2, cy + size + 5))

    def _cleanup(self):
        if self.camera:
            self.camera.stop()
        pygame.quit()
