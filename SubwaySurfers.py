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
import time
import keyboard
import pyautogui

cap = cv2.VideoCapture(0)

hands = mp.solutions.hands.Hands(max_num_hands=1)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
mpDraw = mp.solutions.drawing_utils
screen_width, screen_height = pyautogui.size()

pTime = 0
cTime = 0

# Cooldown tracking (prevents spamming inputs)
cooldowns = {}
COOLDOWN_MS = 400


def cooled_down(action):
    now = time.time() * 1000
    last = cooldowns.get(action, 0)
    if now - last >= COOLDOWN_MS:
        cooldowns[action] = now
        return True
    return False


while not keyboard.is_pressed('q'):
    ret, frame = cap.read()
    if not ret:
        continue

    # Flip first so all processing and drawing is on the mirrored frame
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_h, frame_w, _ = frame.shape

    resultshand = hands.process(rgb_frame)
    resultsface = face_mesh.process(rgb_frame)

    # --- Hand gesture detection ---
    if resultshand.multi_hand_landmarks:
        for handLms in resultshand.multi_hand_landmarks:
            lms = handLms.landmark

            # Thumb tip (id=4)
            thumb_x = int(lms[4].x * frame_w)
            thumb_y = int(lms[4].y * frame_h)
            cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 255, 0))

            # Index finger tip (id=8)
            index_x = int(lms[8].x * frame_w)
            index_y = int(lms[8].y * frame_h)
            cv2.circle(frame, (index_x, index_y), 10, (0, 255, 255))

            # Middle finger tip (id=12)
            middle_x = int(lms[12].x * frame_w)
            middle_y = int(lms[12].y * frame_h)
            cv2.circle(frame, (middle_x, middle_y), 10, (255, 255, 0))

            # Pinch thumb + index = UP (jump)
            if abs(thumb_y - index_y) < 30 and cooled_down("up"):
                keyboard.press_and_release('up')
                print("UP")

            # Pinch thumb + middle = DOWN (slide)
            if abs(thumb_y - middle_y) < 30 and cooled_down("down"):
                keyboard.press_and_release('down')
                print("DOWN")

            mpDraw.draw_landmarks(frame, handLms, mp.solutions.hands.HAND_CONNECTIONS)

    # --- Eye blink detection ---
    if resultsface.multi_face_landmarks:
        landmarks = resultsface.multi_face_landmarks[0].landmark

        # Left eye
        left = [landmarks[145], landmarks[159]]
        for lm in left:
            x = int(lm.x * frame_w)
            y = int(lm.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0))
        if (left[0].y - left[1].y) < 0.004 and cooled_down("left"):
            keyboard.press_and_release('left')
            print("LEFT")

        # Right eye
        right = [landmarks[373], landmarks[386]]
        for lm in right:
            x = int(lm.x * frame_w)
            y = int(lm.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 0, 255))
        if (right[0].y - right[1].y) < 0.004 and cooled_down("right"):
            keyboard.press_and_release('right')
            print("RIGHT")

    # FPS display
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime

    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
    cv2.imshow("Hands and Eyes Controller", frame)
    cv2.waitKey(1)

# Cleanup
cap.release()
hands.close()
face_mesh.close()
cv2.destroyAllWindows()
