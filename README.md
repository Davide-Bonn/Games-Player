<div align="center">

# Games Player

**Camera-controlled gaming platform using hand gestures and facial expressions**

[![Try Live](https://img.shields.io/badge/Play%20Now-games--player--app.vercel.app-00C853?style=for-the-badge&logo=vercel&logoColor=white)](https://games-player-app.vercel.app)

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://mediapipe.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Play classic games with your webcam — no install needed.*

---

</div>

## Games

### Dino Runner

Chrome T-Rex style side-scroller. Jump over cacti and dodge pterodactyls.

![Dino Runner](assets/dino.gif)

---

### Subway Runner

Dodge trains and barriers in this endless 3-lane runner with street-art aesthetic.

![Subway Runner](assets/subway.gif)

---

## Controls

| Gesture | Default Action |
|:---|:---|
| Thumb + Index Pinch | Jump |
| Thumb + Middle Pinch | Slide / Duck |
| Left Eye Blink | Move Left |
| Right Eye Blink | Move Right |
| Both Eyes Blink | Not Assigned |
| Open Mouth | Not Assigned |

> Keyboard controls also work (Arrow keys / WASD, Space to jump).

---

## Settings

Customize gesture-to-action mappings from the settings panel.

![Settings](assets/settings.gif)

---

## Getting Started

### Browser (recommended)

Visit the live demo — all you need is a webcam and a modern browser:

**[games-player-app.vercel.app](https://games-player-app.vercel.app)**

### Desktop

```bash
git clone https://github.com/Davide-Bonn/Games-Player.git
cd Games-Player
pip install -r requirements.txt
python main.py
```

---

## Requirements

| Platform | Requirements |
|:---|:---|
| Web | Modern browser with HTTPS, webcam |
| Desktop | Python 3.8+, opencv-python, mediapipe, pygame |

---

## License

MIT
