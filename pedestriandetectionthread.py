from threading import Thread
import cv2
import numpy as np


class PedestrianDetection:

    def pedestrians(self, pedestrian_tracker, frame_g, frame):
        print("YOU CROSSED THE ZEBRA CROSSING")
        vertices = np.array([[(50, 720), (50, 300), (1200, 300), (1200, 720)]], dtype=np.int32)
        mask = np.zeros_like(frame_g)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(frame_g, mask)
        # cv2.imshow("pesak", masked_image)
        pedestrians = pedestrian_tracker.detectMultiScale(masked_image)
        self.start(pedestrians, frame)

    def start(self, pedestrians, frame):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update(pedestrians, frame), args=())
        t.daemon = True
        t.start()
        return self

    def update(self, pedestrians, frame):
        # keep looping infinitely
        if pedestrians is not None:
            for (x, y, w, h) in pedestrians:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                if pedestrians is not None:
                    print("PEDESTRIAN NEAR ZEBRA CROSSING!!!")
                    # signal.signal(1)
                # else:
                # signal.signal(0)


    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
