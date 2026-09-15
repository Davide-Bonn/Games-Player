# Window - wider to fit camera panel on the right
GAME_WIDTH = 420
CAMERA_PANEL_WIDTH = 250
SCREEN_WIDTH = GAME_WIDTH + CAMERA_PANEL_WIDTH  # 670 total
SCREEN_HEIGHT = 700
FPS = 60

# Camera preview
CAM_PREVIEW_W = 230
CAM_PREVIEW_H = 170
CAM_PREVIEW_X = GAME_WIDTH + 10
CAM_PREVIEW_Y = 10

# Lanes
NUM_LANES = 3
LANE_WIDTH = GAME_WIDTH // NUM_LANES
LANE_CENTERS = [LANE_WIDTH // 2 + i * LANE_WIDTH for i in range(NUM_LANES)]

# Player
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 70
PLAYER_Y = SCREEN_HEIGHT - 140
JUMP_VELOCITY = -15
GRAVITY = 0.8
SLIDE_DURATION_FRAMES = 30
SLIDE_HEIGHT = 30
LANE_LERP = 0.25

# Obstacles
INITIAL_SPEED = 5.0
SPEED_INCREMENT = 0.001
MIN_SPAWN_GAP = 45

# ── Subway Surfers Graffiti Aesthetic ──
# Vibrant, rebellious, street-art inspired palette

# Background & lanes - urban gritty tones
COLOR_BG = (35, 25, 45)
COLOR_PANEL_BG = (25, 18, 35)
COLOR_LANE_1 = (55, 45, 65)
COLOR_LANE_2 = (45, 35, 58)
COLOR_LANE_LINE = (80, 65, 95)
COLOR_LANE_DASH = (110, 85, 130)

# Player - electric cyan/teal like Jake
COLOR_PLAYER = (0, 210, 255)
COLOR_PLAYER_HEAD = (0, 230, 255)
COLOR_PLAYER_SLIDE = (0, 170, 220)
COLOR_PLAYER_OUTLINE = (255, 80, 180)

# Obstacles - bold graffiti colors
COLOR_BARRIER = (255, 55, 85)       # hot pink-red
COLOR_OVERHEAD = (255, 200, 0)      # graffiti yellow
COLOR_TRAIN = (130, 50, 220)        # purple train
COLOR_TRAIN_STRIPE = (255, 100, 200)  # pink stripe
COLOR_TRAIN_WINDOW = (200, 160, 255)

# UI colors
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (170, 160, 180)
COLOR_DARK_GRAY = (100, 90, 110)
COLOR_SCORE = (255, 220, 50)
COLOR_GAMEOVER = (255, 55, 85)
COLOR_MENU_BG = (25, 15, 40)
COLOR_MENU_SEL = (0, 220, 255)
COLOR_ACTIVE = (0, 255, 120)
COLOR_INACTIVE = (70, 55, 85)

# Graffiti accent colors for decorations
COLOR_GRAFFITI_1 = (255, 80, 180)    # hot pink
COLOR_GRAFFITI_2 = (0, 255, 200)     # mint
COLOR_GRAFFITI_3 = (255, 140, 0)     # orange
COLOR_GRAFFITI_4 = (140, 80, 255)    # purple
