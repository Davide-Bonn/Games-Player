# Games Player

Camera-controlled gaming platform using hand gestures and facial expressions. Play classic games with your webcam or keyboard.

## Dino Runner

Chrome T-Rex style side-scroller. Jump over cacti and dodge pterodactyls.

![Dino Runner](dino.gif)

## Subway Runner

Dodge trains and barriers in this endless 3-lane runner with a street-art aesthetic.

![Subway Runner](subway.gif)

## Settings

Customize which gestures map to which game actions. Supports hand pinches, eye blinks, and mouth open/close.

![Settings](Settings_main.gif)

## Controls

| Gesture | Default Action |
|---|---|
| Thumb + Index Pinch | Jump |
| Thumb + Middle Pinch | Slide / Duck |
| Left Eye Blink | Move Left |
| Right Eye Blink | Move Right |
| Both Eyes Blink | Not Assigned |
| Open Mouth | Not Assigned |
| Close Mouth | Not Assigned |

Keyboard controls: Arrow keys or WASD, Space to jump.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Web Version

The web version runs on Vercel or any static host. Camera works client-side via MediaPipe JS over HTTPS.

```bash
cd web
python -m http.server 8000
```

## Requirements

- Python 3.8+
- Webcam (optional, keyboard always works)
- opencv-python, mediapipe, pygame
