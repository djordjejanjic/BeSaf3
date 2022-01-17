from threading import Thread
import cv2
import numpy as np


class PedestrianThread:

    def __init__(self, pedestrian_tracker, frame):
        self.ped = pedestrian_tracker
        self.f = frame
        self.fg = cv2.cvtColor(self.f, cv2.COLOR_BGR2GRAY)

        vertices = np.array([[(50, 720), (50, 300), (1200, 300), (1200, 720)]], dtype=np.int32)
        mask = np.zeros_like(self.fg)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(self.fg, mask)
        self.pedestrians = self.ped.detectMultiScale(masked_image)

    def start(self):
        t1 = Thread(target=self.update)
        t1.daemon = True
        t1.start()
        return self

    def update(self):
        # print("YOU CROSSED THE ZEBRA CROSSING")

        if self.pedestrians is not None:
            for (x, y, w, h) in self.pedestrians:
                cv2.rectangle(self.f, (x, y), (x + w, y + h), (0, 255, 255), 2)
                if self.pedestrians is not None:
                    # print("PEDESTRIAN NEAR ZEBRA CROSSING!!!")
                    continue
                    # signal.signal(1)
                # else:
                # signal.signal(0)
