import pygame
import sys
import os
import math
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    GestureConfig, GESTURES, GESTURE_LABELS, ACTIONS, ACTION_LABELS,
)

# ── Apple-style design tokens ──
BG = (18, 18, 22)
CARD = (28, 28, 34)
CARD_HOVER = (38, 38, 46)
CARD_BORDER = (48, 48, 56)
ACCENT = (0, 122, 255)
ACCENT_HOVER = (30, 142, 255)
ACCENT_2 = (88, 86, 214)
ACCENT_3 = (255, 55, 95)
SUCCESS = (52, 199, 89)
WARNING = (255, 159, 10)
TEXT = (255, 255, 255)
TEXT_2 = (152, 152, 160)
TEXT_3 = (98, 98, 106)
DIVIDER = (44, 44, 50)
PILL_BG = (58, 58, 66)
PILL_ACTIVE = (0, 122, 255)

W, H = 900, 720


def rounded_rect(surf, color, rect, radius=12, border=0, border_color=None):
    r = pygame.Rect(rect)
    if border > 0 and border_color:
        pygame.draw.rect(surf, border_color, r, border_radius=radius)
        inner = r.inflate(-border * 2, -border * 2)
        pygame.draw.rect(surf, color, inner, border_radius=max(1, radius - border))
    else:
        pygame.draw.rect(surf, color, r, border_radius=radius)


class Launcher:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Games Player")
        self.clock = pygame.time.Clock()
        self.config = GestureConfig()

        # Fonts - use Segoe UI on Windows for Apple-like feel
        try:
            self.font_title = pygame.font.SysFont("Segoe UI", 32, bold=True)
            self.font_heading = pygame.font.SysFont("Segoe UI", 22, bold=True)
            self.font_body = pygame.font.SysFont("Segoe UI", 17)
            self.font_small = pygame.font.SysFont("Segoe UI", 14)
            self.font_tiny = pygame.font.SysFont("Segoe UI", 12)
        except Exception:
            self.font_title = pygame.font.SysFont(None, 36, bold=True)
            self.font_heading = pygame.font.SysFont(None, 26, bold=True)
            self.font_body = pygame.font.SysFont(None, 20)
            self.font_small = pygame.font.SysFont(None, 16)
            self.font_tiny = pygame.font.SysFont(None, 14)

        self._tick = 0
        self._hover = None
        self._tutorial_step = 0
        self._tutorial_camera = None
        self._settings_scroll = 0
        self._fade_alpha = 255
        self._result = None

        # Auto-show tutorial on first launch
        if self.config.first_launch:
            self._screen = "tutorial"
            self._start_tutorial_camera()
            self.config.save()  # mark first_launch = False
        else:
            self._screen = "menu"

    def run(self):
        """Returns the selected game mode string or None."""
        while self._result is None:
            self._tick += 1
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._cleanup()
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self._screen != "menu":
                            self._go_back()
                        else:
                            self._cleanup()
                            return None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(mx, my)

            self.screen.fill(BG)

            if self._screen == "menu":
                self._draw_menu(mx, my)
            elif self._screen == "settings":
                self._draw_settings(mx, my)
            elif self._screen == "tutorial":
                self._draw_tutorial(mx, my)

            # Fade in
            if self._fade_alpha > 0:
                overlay = pygame.Surface((W, H), pygame.SRCALPHA)
                overlay.fill((18, 18, 22, self._fade_alpha))
                self.screen.blit(overlay, (0, 0))
                self._fade_alpha = max(0, self._fade_alpha - 15)

            pygame.display.flip()
            self.clock.tick(60)

        self._cleanup()
        return self._result

    def _cleanup(self):
        if self._tutorial_camera:
            self._tutorial_camera.stop()
            self._tutorial_camera = None
        pygame.quit()

    def _go_back(self):
        if self._tutorial_camera:
            self._tutorial_camera.stop()
            self._tutorial_camera = None
        self._screen = "menu"
        self._fade_alpha = 80

    # ── Menu Screen ──

    def _draw_menu(self, mx, my):
        # Title bar
        t = self.font_title.render("Games Player", True, TEXT)
        self.screen.blit(t, (40, 30))

        sub = self.font_small.render("Camera-controlled gaming", True, TEXT_2)
        self.screen.blit(sub, (40, 68))

        # Top-right buttons
        self._draw_pill_button("settings_btn", "Settings", W - 220, 36, 100, 34, mx, my, PILL_BG)
        self._draw_pill_button("tutorial_btn", "Tutorial", W - 110, 36, 90, 34, mx, my, PILL_BG)

        # ── Game cards ──
        card_y = 110
        card_w = (W - 100) // 2
        card_h = 200

        # Subway Runner card
        self._draw_game_card(
            "subway", 30, card_y, card_w, card_h, mx, my,
            title="Subway Runner",
            desc="Dodge trains and barriers in this\nendless 3-lane runner",
            color_accent=ACCENT_2,
            btn1=("subway_kb", "Keyboard"),
            btn2=("subway_cam", "Keyboard + Camera"),
        )

        # Dino Runner card
        self._draw_game_card(
            "dino", card_w + 60, card_y, card_w, card_h, mx, my,
            title="Dino Runner",
            desc="Jump over cacti and dodge birds\nin this side-scrolling classic",
            color_accent=(52, 199, 89),
            btn1=("dino_kb", "Keyboard"),
            btn2=("dino_cam", "Keyboard + Camera"),
        )

        # Online controller card
        online_y = card_y + card_h + 25
        online_rect = pygame.Rect(30, online_y, W - 60, 100)
        hovered = online_rect.collidepoint(mx, my)
        rounded_rect(self.screen, CARD_HOVER if hovered else CARD, online_rect, 14, 1, CARD_BORDER)

        t = self.font_heading.render("Camera Controller", True, TEXT)
        self.screen.blit(t, (50, online_y + 18))
        d = self.font_small.render("Send camera gestures to any focused game window (online play)", True, TEXT_2)
        self.screen.blit(d, (50, online_y + 48))

        self._draw_pill_button("online_btn", "Launch", W - 140, online_y + 30, 90, 36, mx, my, ACCENT_3)

        # Gesture mapping quick preview
        preview_y = online_y + 120
        self._draw_gesture_preview(preview_y)

        # Footer
        foot = self.font_tiny.render("ESC to quit  |  All controls work with arrow keys too", True, TEXT_3)
        self.screen.blit(foot, (W // 2 - foot.get_width() // 2, H - 30))

    def _draw_game_card(self, card_id, x, y, w, h, mx, my,
                        title, desc, color_accent, btn1, btn2):
        rect = pygame.Rect(x, y, w, h)
        hovered = rect.collidepoint(mx, my)
        rounded_rect(self.screen, CARD_HOVER if hovered else CARD, rect, 14, 1, CARD_BORDER)

        # Accent bar at top
        bar = pygame.Rect(x + 1, y + 1, w - 2, 5)
        pygame.draw.rect(self.screen, color_accent, bar,
                         border_top_left_radius=14, border_top_right_radius=14)

        # Title
        t = self.font_heading.render(title, True, TEXT)
        self.screen.blit(t, (x + 20, y + 24))

        # Description
        lines = desc.split("\n")
        for i, line in enumerate(lines):
            d = self.font_small.render(line, True, TEXT_2)
            self.screen.blit(d, (x + 20, y + 56 + i * 20))

        # Buttons
        btn_y = y + h - 58
        self._draw_pill_button(btn1[0], btn1[1], x + 20, btn_y, w // 2 - 30, 36, mx, my, PILL_BG)
        self._draw_pill_button(btn2[0], btn2[1], x + w // 2, btn_y, w // 2 - 20, 36, mx, my, color_accent)

    def _draw_pill_button(self, btn_id, label, x, y, w, h, mx, my, color):
        rect = pygame.Rect(x, y, w, h)
        hovered = rect.collidepoint(mx, my)
        c = tuple(min(255, c + 20) for c in color) if hovered else color
        pygame.draw.rect(self.screen, c, rect, border_radius=h // 2)

        t = self.font_small.render(label, True, TEXT)
        self.screen.blit(t, (x + w // 2 - t.get_width() // 2, y + h // 2 - t.get_height() // 2))

        # Store for click detection
        if not hasattr(self, "_buttons"):
            self._buttons = {}
        self._buttons[btn_id] = rect

    def _draw_gesture_preview(self, y):
        t = self.font_small.render("Current Gesture Mapping", True, TEXT_3)
        self.screen.blit(t, (40, y))

        x = 40
        for gesture in GESTURES:
            action = self.config.mappings.get(gesture, "NONE")
            if action == "NONE":
                continue
            label = f"{GESTURE_LABELS[gesture]}  →  {ACTION_LABELS[action]}"
            chip_w = self.font_tiny.size(label)[0] + 20
            rounded_rect(self.screen, DIVIDER, (x, y + 22, chip_w, 24), 12)
            ct = self.font_tiny.render(label, True, TEXT_2)
            self.screen.blit(ct, (x + 10, y + 26))
            x += chip_w + 8
            if x > W - 100:
                break

    # ── Settings Screen ──

    def _draw_settings(self, mx, my):
        # Back button
        self._draw_pill_button("back_btn", "← Back", 30, 30, 80, 34, mx, my, PILL_BG)

        t = self.font_title.render("Gesture Settings", True, TEXT)
        self.screen.blit(t, (130, 26))

        sub = self.font_small.render("Click an action to cycle through options", True, TEXT_2)
        self.screen.blit(sub, (130, 64))

        # Gesture mapping rows
        row_y = 110
        row_h = 72

        for i, gesture in enumerate(GESTURES):
            ry = row_y + i * row_h
            action = self.config.mappings.get(gesture, "NONE")

            # Row background
            row_rect = pygame.Rect(30, ry, W - 60, row_h - 6)
            hovered = row_rect.collidepoint(mx, my)
            rounded_rect(self.screen, CARD_HOVER if hovered else CARD, row_rect, 12, 1, CARD_BORDER)

            # Gesture icon (simple illustration)
            self._draw_gesture_icon(50, ry + 10, gesture, 44)

            # Gesture label
            gl = self.font_body.render(GESTURE_LABELS[gesture], True, TEXT)
            self.screen.blit(gl, (110, ry + 12))

            # Gesture description
            desc = self._gesture_description(gesture)
            gd = self.font_tiny.render(desc, True, TEXT_3)
            self.screen.blit(gd, (110, ry + 36))

            # Action button (clickable, cycles through actions)
            action_color = ACCENT if action != "NONE" else PILL_BG
            btn_id = f"action_{gesture}"
            action_label = ACTION_LABELS[action]
            self._draw_pill_button(btn_id, action_label, W - 220, ry + 16, 170, 34, mx, my, action_color)

        # Bottom buttons
        btn_y = row_y + len(GESTURES) * row_h + 15
        self._draw_pill_button("save_btn", "Save", W // 2 - 120, btn_y, 100, 40, mx, my, SUCCESS)
        self._draw_pill_button("reset_btn", "Reset Defaults", W // 2 + 20, btn_y, 140, 40, mx, my, PILL_BG)

    def _gesture_description(self, gesture):
        descs = {
            "pinch_index": "Touch your thumb tip to your index finger tip",
            "pinch_middle": "Touch your thumb tip to your middle finger tip",
            "left_blink": "Close only your left eye",
            "right_blink": "Close only your right eye",
            "both_blink": "Close both eyes briefly",
            "mouth_open": "Open your mouth wide",
            "mouth_close": "Close your mouth after opening it",
        }
        return descs.get(gesture, "")

    def _draw_gesture_icon(self, x, y, gesture, size):
        """Draw a small illustration for each gesture type."""
        cx = x + size // 2
        cy = y + size // 2
        r = size // 2 - 2

        if gesture in ("left_blink", "right_blink", "both_blink"):
            # Face outline
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy), r, 2)
            # Eyes
            le_x, re_x = cx - r // 3, cx + r // 3
            ey = cy - 3
            left_closed = gesture in ("left_blink", "both_blink")
            right_closed = gesture in ("right_blink", "both_blink")

            if left_closed:
                pygame.draw.line(self.screen, ACCENT, (le_x - 5, ey), (le_x + 5, ey), 2)
            else:
                pygame.draw.circle(self.screen, TEXT, (le_x, ey), 4)
                pygame.draw.circle(self.screen, BG, (le_x, ey), 2)

            if right_closed:
                pygame.draw.line(self.screen, ACCENT, (re_x - 5, ey), (re_x + 5, ey), 2)
            else:
                pygame.draw.circle(self.screen, TEXT, (re_x, ey), 4)
                pygame.draw.circle(self.screen, BG, (re_x, ey), 2)

            # Mouth
            pygame.draw.arc(self.screen, TEXT_3, (cx - 6, cy + 4, 12, 8), 3.14, 6.28, 1)

        elif gesture == "mouth_open":
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy), r, 2)
            pygame.draw.circle(self.screen, TEXT, (cx - r // 3, cy - 4), 3)
            pygame.draw.circle(self.screen, TEXT, (cx + r // 3, cy - 4), 3)
            pygame.draw.ellipse(self.screen, ACCENT, (cx - 6, cy + 3, 12, 10))
            pygame.draw.ellipse(self.screen, BG, (cx - 4, cy + 5, 8, 6))

        elif gesture == "mouth_close":
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy), r, 2)
            pygame.draw.circle(self.screen, TEXT, (cx - r // 3, cy - 4), 3)
            pygame.draw.circle(self.screen, TEXT, (cx + r // 3, cy - 4), 3)
            # Closed mouth line
            pygame.draw.line(self.screen, ACCENT, (cx - 5, cy + 6), (cx + 5, cy + 6), 2)

        elif gesture == "pinch_index":
            # Hand: thumb + index touching
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy - 4), 5, 2)  # pinch point
            pygame.draw.line(self.screen, TEXT_3, (cx, cy + 1), (cx - 6, cy + r), 2)  # thumb
            pygame.draw.line(self.screen, TEXT_3, (cx, cy + 1), (cx + 2, cy + r), 2)  # index
            pygame.draw.line(self.screen, ACCENT, (cx - 1, cy - 4), (cx + 1, cy - 4), 3)  # touch
            # Other fingers
            pygame.draw.line(self.screen, TEXT_3, (cx + 4, cy + 2), (cx + 8, cy + r - 4), 1)
            pygame.draw.line(self.screen, TEXT_3, (cx + 6, cy + 4), (cx + 10, cy + r - 2), 1)

        elif gesture == "pinch_middle":
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy - 4), 5, 2)
            pygame.draw.line(self.screen, TEXT_3, (cx, cy + 1), (cx - 6, cy + r), 2)
            pygame.draw.line(self.screen, TEXT_3, (cx - 2, cy + 1), (cx - 4, cy + r - 2), 1)  # index free
            pygame.draw.line(self.screen, TEXT_3, (cx, cy + 1), (cx + 2, cy + r), 2)  # middle
            pygame.draw.line(self.screen, ACCENT_2, (cx - 1, cy - 4), (cx + 1, cy - 4), 3)

    # ── Tutorial Screen ──

    def _draw_tutorial(self, mx, my):
        self._draw_pill_button("back_btn", "← Back", 30, 30, 80, 34, mx, my, PILL_BG)

        t = self.font_title.render("Tutorial", True, TEXT)
        self.screen.blit(t, (130, 26))

        step = self._tutorial_step
        total = len(GESTURES)
        active_gestures_in_step = self._get_active_mapped_gestures()

        # Step counter
        counter = self.font_small.render(f"Step {step + 1} of {total}", True, TEXT_2)
        self.screen.blit(counter, (W - 140, 36))

        # Progress dots
        for i in range(total):
            dx = W // 2 - (total * 16) // 2 + i * 16
            color = ACCENT if i <= step else DIVIDER
            pygame.draw.circle(self.screen, color, (dx + 6, 80), 5 if i == step else 3)

        gesture = GESTURES[step]
        action = self.config.mappings.get(gesture, "NONE")

        # Main content area
        content_y = 100

        # Left side: camera feed
        cam_rect = pygame.Rect(40, content_y, 340, 260)
        rounded_rect(self.screen, CARD, cam_rect, 14, 1, CARD_BORDER)

        if self._tutorial_camera:
            surf = self._tutorial_camera.get_pygame_surface(330, 250)
            self.screen.blit(surf, (45, content_y + 5))
        else:
            msg = self.font_body.render("Starting camera...", True, TEXT_3)
            self.screen.blit(msg, (cam_rect.centerx - msg.get_width() // 2,
                                   cam_rect.centery - msg.get_height() // 2))

        # Right side: gesture info
        info_x = 410
        info_y = content_y + 10

        # Large gesture icon
        self._draw_gesture_icon_large(info_x + 20, info_y, gesture)

        # Gesture name
        gn = self.font_heading.render(GESTURE_LABELS[gesture], True, TEXT)
        self.screen.blit(gn, (info_x + 120, info_y + 10))

        # Mapped action
        if action != "NONE":
            aa = self.font_body.render(f"Mapped to: {ACTION_LABELS[action]}", True, ACCENT)
        else:
            aa = self.font_body.render("Not assigned (skip)", True, TEXT_3)
        self.screen.blit(aa, (info_x + 120, info_y + 42))

        # Description
        desc = self._gesture_description(gesture)
        dd = self.font_body.render(desc, True, TEXT_2)
        self.screen.blit(dd, (info_x + 20, info_y + 90))

        # Detection status
        detected = gesture in active_gestures_in_step
        status_y = info_y + 140

        if detected:
            pulse = int(abs(math.sin(self._tick * 0.1)) * 30)
            status_color = (52 + pulse, 199 + min(56, pulse), 89 + pulse)
            pygame.draw.circle(self.screen, status_color, (info_x + 30, status_y + 8), 8)
            st = self.font_body.render("Detected!", True, SUCCESS)
        else:
            pygame.draw.circle(self.screen, TEXT_3, (info_x + 30, status_y + 8), 8, 2)
            st = self.font_body.render("Try the gesture now...", True, TEXT_3)
        self.screen.blit(st, (info_x + 48, status_y))

        # Tip box
        tip_y = content_y + 280
        tip_rect = pygame.Rect(40, tip_y, W - 80, 60)
        rounded_rect(self.screen, (35, 35, 20), tip_rect, 12, 1, (60, 60, 30))

        tip_label = self.font_small.render("Tip", True, WARNING)
        self.screen.blit(tip_label, (60, tip_y + 8))

        tips = {
            "pinch_index": "Hold your hand up clearly and slowly bring thumb and index together",
            "pinch_middle": "Keep index finger extended while touching thumb to middle finger",
            "left_blink": "Try to close just your left eye — keep the right one open",
            "right_blink": "Close just your right eye — keep the left one open",
            "both_blink": "Close both eyes at the same time for a brief moment",
            "mouth_open": "Open your mouth wide — like you're saying 'aah'",
            "mouth_close": "Open your mouth first, then close it — the close triggers the action",
        }
        tip_text = self.font_small.render(tips.get(gesture, ""), True, TEXT_2)
        self.screen.blit(tip_text, (60, tip_y + 30))

        # Navigation buttons
        nav_y = H - 70
        if step > 0:
            self._draw_pill_button("tut_prev", "← Previous", 40, nav_y, 120, 40, mx, my, PILL_BG)
        if step < total - 1:
            self._draw_pill_button("tut_next", "Next →", W - 160, nav_y, 120, 40, mx, my, ACCENT)
        else:
            self._draw_pill_button("tut_done", "Done", W - 160, nav_y, 120, 40, mx, my, SUCCESS)

    def _draw_gesture_icon_large(self, x, y, gesture):
        """Draw a larger, more detailed gesture illustration."""
        size = 80
        cx = x + size // 2
        cy = y + size // 2
        r = 35

        bg_rect = pygame.Rect(x, y, size, size)
        rounded_rect(self.screen, CARD, bg_rect, 16, 1, CARD_BORDER)

        if gesture in ("left_blink", "right_blink", "both_blink"):
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy), r, 2)
            le_x, re_x = cx - 12, cx + 12
            ey = cy - 5
            left_closed = gesture in ("left_blink", "both_blink")
            right_closed = gesture in ("right_blink", "both_blink")

            if left_closed:
                pygame.draw.line(self.screen, ACCENT, (le_x - 8, ey), (le_x + 8, ey), 3)
                # Eyelash marks
                pygame.draw.line(self.screen, ACCENT, (le_x - 6, ey - 2), (le_x - 4, ey), 1)
                pygame.draw.line(self.screen, ACCENT, (le_x + 6, ey - 2), (le_x + 4, ey), 1)
            else:
                pygame.draw.circle(self.screen, TEXT, (le_x, ey), 6)
                pygame.draw.circle(self.screen, BG, (le_x, ey), 3)

            if right_closed:
                pygame.draw.line(self.screen, ACCENT, (re_x - 8, ey), (re_x + 8, ey), 3)
                pygame.draw.line(self.screen, ACCENT, (re_x - 6, ey - 2), (re_x - 4, ey), 1)
                pygame.draw.line(self.screen, ACCENT, (re_x + 6, ey - 2), (re_x + 4, ey), 1)
            else:
                pygame.draw.circle(self.screen, TEXT, (re_x, ey), 6)
                pygame.draw.circle(self.screen, BG, (re_x, ey), 3)

            pygame.draw.arc(self.screen, TEXT_3, (cx - 8, cy + 6, 16, 10), 3.14, 6.28, 2)

        elif gesture == "mouth_open":
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy), r, 2)
            pygame.draw.circle(self.screen, TEXT, (cx - 12, cy - 6), 5)
            pygame.draw.circle(self.screen, BG, (cx - 12, cy - 6), 2)
            pygame.draw.circle(self.screen, TEXT, (cx + 12, cy - 6), 5)
            pygame.draw.circle(self.screen, BG, (cx + 12, cy - 6), 2)
            pygame.draw.ellipse(self.screen, ACCENT, (cx - 10, cy + 4, 20, 16))
            pygame.draw.ellipse(self.screen, BG, (cx - 7, cy + 7, 14, 10))

        elif gesture == "mouth_close":
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy), r, 2)
            pygame.draw.circle(self.screen, TEXT, (cx - 12, cy - 6), 5)
            pygame.draw.circle(self.screen, BG, (cx - 12, cy - 6), 2)
            pygame.draw.circle(self.screen, TEXT, (cx + 12, cy - 6), 5)
            pygame.draw.circle(self.screen, BG, (cx + 12, cy - 6), 2)
            # Closed mouth
            pygame.draw.line(self.screen, ACCENT, (cx - 8, cy + 8), (cx + 8, cy + 8), 3)
            # Small arrow down to show "closing"
            pygame.draw.line(self.screen, TEXT_3, (cx, cy + 14), (cx - 4, cy + 18), 1)
            pygame.draw.line(self.screen, TEXT_3, (cx, cy + 14), (cx + 4, cy + 18), 1)

        elif gesture == "pinch_index":
            # Larger hand illustration
            # Palm
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy + 8), 14, 2)
            # Thumb going up-left
            pygame.draw.line(self.screen, TEXT_3, (cx - 10, cy), (cx - 4, cy - 18), 3)
            # Index going up-right to meet thumb
            pygame.draw.line(self.screen, TEXT_3, (cx - 2, cy - 2), (cx - 2, cy - 18), 3)
            # Touch point
            pygame.draw.circle(self.screen, ACCENT, (cx - 3, cy - 20), 5)
            pygame.draw.circle(self.screen, ACCENT, (cx - 3, cy - 20), 3)
            # Other fingers
            pygame.draw.line(self.screen, TEXT_3, (cx + 4, cy - 2), (cx + 6, cy - 14), 2)
            pygame.draw.line(self.screen, TEXT_3, (cx + 9, cy), (cx + 12, cy - 10), 2)
            pygame.draw.line(self.screen, TEXT_3, (cx + 13, cy + 4), (cx + 16, cy - 4), 2)

        elif gesture == "pinch_middle":
            pygame.draw.circle(self.screen, TEXT_3, (cx, cy + 8), 14, 2)
            # Thumb
            pygame.draw.line(self.screen, TEXT_3, (cx - 10, cy), (cx - 2, cy - 18), 3)
            # Index (free, pointing up)
            pygame.draw.line(self.screen, TEXT_3, (cx - 4, cy - 2), (cx - 6, cy - 22), 2)
            # Middle going to meet thumb
            pygame.draw.line(self.screen, TEXT_3, (cx + 2, cy - 2), (cx, cy - 18), 3)
            # Touch point
            pygame.draw.circle(self.screen, ACCENT_2, (cx - 1, cy - 20), 5)
            pygame.draw.circle(self.screen, ACCENT_2, (cx - 1, cy - 20), 3)
            # Ring, pinky
            pygame.draw.line(self.screen, TEXT_3, (cx + 8, cy), (cx + 10, cy - 10), 2)
            pygame.draw.line(self.screen, TEXT_3, (cx + 13, cy + 4), (cx + 14, cy - 4), 2)

    def _get_active_mapped_gestures(self):
        if self._tutorial_camera:
            return self._tutorial_camera.get_active_gestures()
        return set()

    # ── Click handling ──

    def _handle_click(self, mx, my):
        if not hasattr(self, "_buttons"):
            return

        for btn_id, rect in self._buttons.items():
            if not rect.collidepoint(mx, my):
                continue

            # Menu buttons
            if btn_id == "settings_btn":
                self._screen = "settings"
                self._fade_alpha = 80
            elif btn_id == "tutorial_btn":
                self._screen = "tutorial"
                self._tutorial_step = 0
                self._fade_alpha = 80
                self._start_tutorial_camera()
            elif btn_id == "subway_kb":
                self._result = "subway_kb"
            elif btn_id == "subway_cam":
                self._result = "subway_cam"
            elif btn_id == "dino_kb":
                self._result = "dino_kb"
            elif btn_id == "dino_cam":
                self._result = "dino_cam"
            elif btn_id == "online_btn":
                self._result = "online"

            # Settings buttons
            elif btn_id == "back_btn":
                self._go_back()
            elif btn_id.startswith("action_"):
                gesture = btn_id[7:]
                self._cycle_action(gesture)
            elif btn_id == "save_btn":
                self.config.save()
                self._go_back()
            elif btn_id == "reset_btn":
                self.config.reset()

            # Tutorial buttons
            elif btn_id == "tut_prev":
                self._tutorial_step = max(0, self._tutorial_step - 1)
            elif btn_id == "tut_next":
                self._tutorial_step = min(len(GESTURES) - 1, self._tutorial_step + 1)
            elif btn_id == "tut_done":
                self._go_back()

            break

        # Clear buttons for next frame
        self._buttons = {}

    def _cycle_action(self, gesture):
        current = self.config.mappings.get(gesture, "NONE")
        idx = ACTIONS.index(current) if current in ACTIONS else -1
        next_idx = (idx + 1) % len(ACTIONS)
        self.config.set_mapping(gesture, ACTIONS[next_idx])

    def _start_tutorial_camera(self):
        if self._tutorial_camera:
            return
        try:
            from camera_controller import CameraController
            self._tutorial_camera = CameraController(cooldown_ms=300, show_preview=False, config=self.config)
            self._tutorial_camera.start()
        except Exception:
            self._tutorial_camera = None
