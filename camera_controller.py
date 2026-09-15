import os
import sys

os.environ["GLOG_minloglevel"] = "3"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

_stderr = sys.stderr
sys.stderr = open(os.devnull, "w")
try:
    import mediapipe as mp
finally:
    sys.stderr.close()
    sys.stderr = _stderr

import cv2
import numpy as np
import threading
import queue
import time
from config import GestureConfig


class CameraController:
    """Threaded camera input with configurable gesture-to-action mapping."""

    def __init__(self, cooldown_ms=400, show_preview=False, config=None):
        self.cooldown_ms = cooldown_ms
        self.show_preview = show_preview
        self.config = config or GestureConfig()

        self._cap = cv2.VideoCapture(0)
        self._hands = mp.solutions.hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )
        self._face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        self._action_queue = queue.Queue()
        self._cooldowns = {}
        self._running = False
        self._thread = None
        self._current_frame = None
        self._lock = threading.Lock()

        # Track active gestures for UI feedback {gesture_name: timestamp}
        self._active_gestures = {}
        self._active_duration_ms = 500
        # Mouth state tracking for open/close detection
        self._mouth_was_open = False

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=3)
        self._cap.release()
        self._hands.close()
        self._face_mesh.close()
        if self.show_preview:
            cv2.destroyAllWindows()

    def get_actions(self):
        actions = []
        while True:
            try:
                actions.append(self._action_queue.get_nowait())
            except queue.Empty:
                break
        return actions

    def get_active_gestures(self):
        """Return set of gesture names that fired recently."""
        now = time.time() * 1000
        with self._lock:
            return {g for g, t in self._active_gestures.items()
                    if now - t < self._active_duration_ms}

    def get_active_actions(self):
        """Return set of action names that fired recently (for backward compat)."""
        gestures = self.get_active_gestures()
        actions = set()
        for g in gestures:
            a = self.config.get_action(g)
            if a:
                actions.add(a)
        return actions

    def get_frame(self):
        with self._lock:
            return self._current_frame.copy() if self._current_frame is not None else None

    def get_pygame_surface(self, width, height):
        import pygame
        frame = self.get_frame()
        if frame is None:
            surf = pygame.Surface((width, height))
            surf.fill((30, 30, 30))
            return surf
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (width, height))
        surf = pygame.surfarray.make_surface(np.transpose(frame, (1, 0, 2)))
        return surf

    def reload_config(self):
        self.config = GestureConfig()

    def _loop(self):
        while self._running:
            ok, frame = self._cap.read()
            if not ok:
                time.sleep(0.01)
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            hand_result = self._hands.process(rgb)
            face_result = self._face_mesh.process(rgb)

            self._detect_all(hand_result, face_result)
            self._draw_debug(frame, hand_result, face_result)

            if self.show_preview:
                cv2.imshow("Camera Controller", frame)
                cv2.waitKey(1)

            with self._lock:
                self._current_frame = frame

    def _detect_all(self, hand_result, face_result):
        # ── Hand gestures ──
        if hand_result.multi_hand_landmarks:
            lms = hand_result.multi_hand_landmarks[0].landmark
            thumb_y = lms[4].y
            index_y = lms[8].y
            middle_y = lms[12].y

            if abs(thumb_y - index_y) < 0.045:
                self._emit_gesture("pinch_index")
            if abs(thumb_y - middle_y) < 0.045:
                self._emit_gesture("pinch_middle")

        # ── Face gestures ──
        if face_result.multi_face_landmarks:
            lm = face_result.multi_face_landmarks[0].landmark
            left_gap = lm[145].y - lm[159].y
            right_gap = lm[373].y - lm[386].y
            left_closed = left_gap < 0.004
            right_closed = right_gap < 0.004

            # Both eyes blink (check first, more specific)
            if left_closed and right_closed:
                self._emit_gesture("both_blink")
            else:
                if left_closed:
                    self._emit_gesture("left_blink")
                if right_closed:
                    self._emit_gesture("right_blink")

            # Mouth open/close (upper lip 13, lower lip 14)
            mouth_gap = abs(lm[13].y - lm[14].y)
            mouth_is_open = mouth_gap > 0.03
            if mouth_is_open:
                self._emit_gesture("mouth_open")
            if self._mouth_was_open and not mouth_is_open:
                self._emit_gesture("mouth_close")
            self._mouth_was_open = mouth_is_open

    def _emit_gesture(self, gesture_name):
        """Map gesture to action via config, then emit if cooled down."""
        action = self.config.get_action(gesture_name)
        if action is None:
            return

        now = time.time() * 1000
        # Cooldown per gesture (not per action) to avoid conflicts
        last = self._cooldowns.get(gesture_name, 0)
        if now - last >= self.cooldown_ms:
            self._cooldowns[gesture_name] = now
            self._action_queue.put(action)
            with self._lock:
                self._active_gestures[gesture_name] = now

    def _draw_debug(self, frame, hand_result, face_result):
        h, w, _ = frame.shape
        mp_draw = mp.solutions.drawing_utils

        if hand_result.multi_hand_landmarks:
            for hand_lms in hand_result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_lms, mp.solutions.hands.HAND_CONNECTIONS)

        if face_result.multi_face_landmarks:
            lm = face_result.multi_face_landmarks[0].landmark
            for idx in [145, 159]:
                x, y = int(lm[idx].x * w), int(lm[idx].y * h)
                cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)
            for idx in [373, 386]:
                x, y = int(lm[idx].x * w), int(lm[idx].y * h)
                cv2.circle(frame, (x, y), 3, (0, 0, 255), -1)
            # Mouth landmarks
            for idx in [13, 14]:
                x, y = int(lm[idx].x * w), int(lm[idx].y * h)
                cv2.circle(frame, (x, y), 3, (255, 255, 0), -1)


def run_external_controller():
    """Run camera controller sending keyboard events to focused window."""
    import keyboard as kb

    print("Camera Controller (External Mode)")
    print("Press 'q' to quit.\n")

    controller = CameraController(cooldown_ms=400, show_preview=True)
    controller.start()

    try:
        while not kb.is_pressed("q"):
            actions = controller.get_actions()
            for action in actions:
                key = action.lower()
                print(f"  -> {action}")
                kb.press_and_release(key)
            time.sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()
        print("Controller stopped.")
