import cv2
import numpy as np


def verify_alpha_channel(frame):
    try:
        frame.shape[3]
    except:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    return frame


def apply_color(frame, intensity, blue, green, red):
    frame = verify_alpha_channel(frame)
    frame_h, frame_w, frame_c = frame.shape
    color_bgra = (blue, green, red, 1)
    overlay = np.full((frame_h, frame_w, 4), color_bgra, dtype='uint8')
    cv2.addWeighted(overlay, intensity, frame, 1.0, 0, frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    return frame
