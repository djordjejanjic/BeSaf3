from threading import Thread
import cv2
import numpy as np

from globals.globals import Globals


class StopSignThread:

    def __init__(self, stop_sign_tracker, frame, previous):
        self.x = None
        self.y = None
        self.w = None
        self.h = None
        self.previous = previous
        self.stop_tracker = stop_sign_tracker
        self.f = frame
        self.fg = cv2.cvtColor(self.f, cv2.COLOR_BGR2GRAY)

        vertices = np.array([[(860, 550), (860, 140), (1200, 140), (1200, 550)]], dtype=np.int32)
        mask = np.zeros_like(self.fg)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(self.fg, mask)
        self.stop = stop_sign_tracker.detectMultiScale(masked_image)
        # cv2.imshow("znaktest", masked_image)

        vertices_stop = np.array([[(860, 400), (860, 140), (1200, 140), (1200, 400)]], dtype=np.int32)
        mask_stop = np.zeros_like(self.fg)
        cv2.fillPoly(mask_stop, vertices_stop, 255)
        self.masked_image_stop = cv2.bitwise_and(self.fg, mask_stop)

    def start(self):
        t1 = Thread(target=self.update)
        t1.daemon = True
        t1.start()
        return self

    def update(self):
        if self.stop is not None:
            for (x, y, w, h) in self.stop:
                # cv2.rectangle(self.f, (x, y), (x + w, y + h), (255, 0, 255), 2)
                self.x = x
                self.y = y
                self.w = w
                self.h = h
                # signal.signal(1)
                # print("ZNAK STOP")

                if self.previous is not None:
                    diff = cv2.absdiff(self.previous, self.masked_image_stop)
                    # cv2.imshow("diff", diff)
                    if np.sum(diff) != 0:
                        print("STOP!!!")
                        # signal.signal(1)
                    else:
                        print("DRIVER HAS STOPPED!")
                self.previous = self.masked_image_stop
        # else:
        # signal.signal(0)
