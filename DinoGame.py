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
import pyautogui
import keyboard
import time

pTime = 0

cam = cv2.VideoCapture(0)
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
screen_w, screen_h = pyautogui.size()
while keyboard.is_pressed('q') == False:
    _, frame = cam.read()
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    output = face_mesh.process(rgb_frame)
    landmark_points = output.multi_face_landmarks
    frame_h, frame_w, _ = frame.shape
    if landmark_points:
        landmarks = landmark_points[0].landmark
        for id, landmark in enumerate(landmarks[474:478]):
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 0, 255))

        left = [landmarks[145], landmarks[159]]
        for landmark in left:
            x = int(landmark.x * frame_w)
            y = int(landmark.y * frame_h)
            cv2.circle(frame, (x, y), 3, (0, 0, 255))        
        if (left[0].y - left[1].y) < 0.004:
            keyboard.press_and_release("up arrow", do_release = 1.5)
        
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(frame, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 3)
    cv2.imshow('Eye Controlled controller', frame)
    cv2.waitKey(1)

    
