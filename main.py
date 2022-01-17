import cv2
import numpy as np
# import signal as signal

from globals.globals import Globals
from utility.static_car_detection import StaticCarDetection
from utility.effects import apply_color
from utility.line_detection import lineDetector
from threads.streamthread import FileVideoStream
from threads.car_detection import CarThread
from threads.pedestrian_detection import PedestrianThread
from threads.stop_sign_detection import StopSignThread

stream = FileVideoStream(Globals.path).start()


def startVideo(db):
    car_tracker = cv2.CascadeClassifier(Globals.classifierCars)
    pedestrian_tracker = cv2.CascadeClassifier(Globals.classifierPedestrian)
    stop_tracker = cv2.CascadeClassifier(Globals.classifierStopSign)

    # Detektuje samo automobile isped i meri distancu
    previous_distance = 0
    safe_distance = 800
    know_distance = 800  # centimetri
    know_width = 150
    fonts = cv2.FONT_HERSHEY_COMPLEX

    def focalLength(measured_distance, real_width, width_in_rf_image):
        focal_length = (width_in_rf_image * measured_distance) / real_width
        return focal_length

    def distanceFinder(focal_length, real_car_width, car_width_in_frame):
        distance = (real_car_width * focal_length) / car_width_in_frame
        return distance

    ref_image = cv2.imread("assets/refimage1.png")
    ref_image_car_width = StaticCarDetection().detectCarInImg(ref_image, car_tracker)

    focal_length_found = focalLength(know_distance, know_width, ref_image_car_width)
    foc = focal_length_found[0][0][0]

    while stream.more():

        frame = stream.read()

        Globals.result = Globals.result + 25
        line_frame = lineDetector(frame)

        carDet = CarThread(car_tracker, frame)
        carDetection = carDet.detectCars()

        carDetectionWidth = Globals.car_width_global

        cv2.putText(carDetection, f"Result: {Globals.result}", (800, 50), fonts, 1.2, (0, 0, 255), 2)
        if carDetectionWidth != 0:

            Distance = distanceFinder(foc, know_width, carDetectionWidth)
            DistanceInCM = round(Distance)
            cv2.putText(carDetection, f"Distance: {DistanceInCM} cm", (50, 50), fonts, 0.6, (255, 255, 255), 2)

            if Distance < safe_distance:
                if previous_distance != Distance:
                    previous_distance = Distance
                    cv2.putText(carDetection, "WARNING! SLOW DOWN!", (400, 650), fonts, 1.2, (0, 0, 255), 2)
                    blue = 230
                    intensity = 0.3
                    Globals.result = Globals.result - 15
                    carDetection = apply_color(carDetection, intensity, blue, 0, 0)
        else:
            cv2.putText(carDetection, f"Not available", (50, 50), fonts, 0.6, (255, 255, 255), 2)

        image_whole = cv2.addWeighted(carDetection, 1, line_frame, 1, 0)

        # formatiraj za prikaz u pretrazivacu
        imgCode = cv2.imencode('.jpg', image_whole)[1]
        stringData = imgCode.tostring()
        yield b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n'

        # print("SIGNAL ", signal)
        # global signal
        if Globals.signal == 1:
            # operations.insert(result)
            break

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            db.insert(Globals.result)
            break

        stream.stop()
        cv2.destroyAllWindows()


def stopAndSave(db):
    db.insert(Globals.result)
    Globals.signal = 1
    stream.stop()
    cv2.destroyAllWindows()


def restart():
    Globals.signal = 0
