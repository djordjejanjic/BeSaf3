from threading import Thread
import cv2
import numpy as np
from globals.globals import Globals


class CarThread:

    def __init__(self, car_tracker, frame):
        self.car_tracker = car_tracker
        self.frame = frame

    def detectCars(self):

        frame_g = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        # maskiranje
        # vertices = np.array([[(550,600),(550, 300), (750, 300), (750,600)]], dtype=np.int32)
        vertices = np.array([[(520, 600), (550, 330), (750, 330), (780, 600)]], dtype=np.int32)
        mask = np.zeros_like(frame_g)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(frame_g, mask)

        cars = self.car_tracker.detectMultiScale(masked_image, minSize=(50, 50))

        for (x, y, w, h) in cars:
            # cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            Globals.car_width_global = w

        return self.frame

