import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gesture_config.json")

# All available gestures the camera can detect
GESTURES = [
    "pinch_index",
    "pinch_middle",
    "left_blink",
    "right_blink",
    "both_blink",
    "mouth_open",
    "mouth_close",
]

GESTURE_LABELS = {
    "pinch_index": "Thumb + Index Pinch",
    "pinch_middle": "Thumb + Middle Pinch",
    "left_blink": "Left Eye Blink",
    "right_blink": "Right Eye Blink",
    "both_blink": "Both Eyes Blink",
    "mouth_open": "Open Mouth",
    "mouth_close": "Close Mouth",
}

# All available game actions
ACTIONS = ["JUMP", "SLIDE", "LEFT", "RIGHT", "NONE"]

ACTION_LABELS = {
    "JUMP": "Jump",
    "SLIDE": "Slide / Duck",
    "LEFT": "Move Left",
    "RIGHT": "Move Right",
    "NONE": "Not Assigned",
}

ACTION_TO_KEY = {
    "JUMP": "UP",
    "SLIDE": "DOWN",
    "LEFT": "LEFT",
    "RIGHT": "RIGHT",
    "NONE": None,
}

DEFAULT_MAPPINGS = {
    "pinch_index": "JUMP",
    "pinch_middle": "SLIDE",
    "left_blink": "LEFT",
    "right_blink": "RIGHT",
    "both_blink": "NONE",
    "mouth_open": "NONE",
    "mouth_close": "NONE",
}


class GestureConfig:
    def __init__(self):
        self.mappings = dict(DEFAULT_MAPPINGS)
        self.first_launch = True
        self.load()

    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r") as f:
                    data = json.load(f)
                saved = data.get("gestures", {})
                for g in GESTURES:
                    if g in saved and saved[g] in ACTIONS:
                        self.mappings[g] = saved[g]
                self.first_launch = data.get("first_launch", True)
            except (json.JSONDecodeError, IOError):
                pass

    def save(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "gestures": self.mappings,
                "first_launch": False,
            }, f, indent=2)

    def reset(self):
        self.mappings = dict(DEFAULT_MAPPINGS)
        self.save()

    def get_action(self, gesture):
        action = self.mappings.get(gesture, "NONE")
        return ACTION_TO_KEY.get(action)

    def set_mapping(self, gesture, action):
        if gesture in GESTURES and action in ACTIONS:
            self.mappings[gesture] = action
