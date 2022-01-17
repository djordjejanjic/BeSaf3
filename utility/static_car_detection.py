import cv2


class StaticCarDetection:

    @staticmethod
    def detectCarInImg(img, car_tracker):
        frame_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cars = car_tracker.detectMultiScale(frame_g)

        for (x, y, w, h) in cars:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return img
