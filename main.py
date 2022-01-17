import cv2
import numpy as np
# from controller.controller import Controller
# from controller.db.operations import DBBroker
# import signal as signal
from globals.globals import Globals
from threads.streamthread import FileVideoStream
from threads.pedestrian_detection import PedestrianThread
from threads.stop_sign_detection import StopSignThread


stream = FileVideoStream('assets/test-vozilo.mp4').start()


def startVideo(db):
    classifierCars = 'models/cars.xml'
    classifierPedestrian = 'models/pedestrian.xml'
    classifierStopSign = 'models/stopsign_classifier.xml'

    car_tracker = cv2.CascadeClassifier(classifierCars)
    pedestrian_tracker = cv2.CascadeClassifier(classifierPedestrian)
    stop_tracker = cv2.CascadeClassifier(classifierStopSign)

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

    def detectCars(frame):

        frame_g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # maskiranje
        # vertices = np.array([[(550,600),(550, 300), (750, 300), (750,600)]], dtype=np.int32)
        vertices = np.array([[(520, 600), (550, 330), (750, 330), (780, 600)]], dtype=np.int32)
        mask = np.zeros_like(frame_g)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(frame_g, mask)

        cars = car_tracker.detectMultiScale(masked_image, minSize=(50, 50))

        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            Globals.car_width_global = w

        return frame

    def detectCarInImg(img):

        frame_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cars = car_tracker.detectMultiScale(frame_g)

        for (x, y, w, h) in cars:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

        return img

    def lineHit(line_image):

        # maska za linije
        # maska za videodriving1 i detekciju pesaka
        # vertices = np.array([[(320,300),(350, 280), (420, 280), (450,300)]], dtype=np.int32)
        # maska za videodriving3
        # vertices = np.array([[(430,510),(500, 450), (650, 450), (750,510)]], dtype=np.int32)
        vertices = np.array([[(580, 610), (650, 580), (720, 580), (790, 610)]], dtype=np.int32)
        mask = np.zeros_like(line_image)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(line_image, mask)

        if np.sum(masked_image) != 0:
            Globals.lineHitCounter = 1
            # signal.signal(lineHitCounter)
            Globals.result = Globals.result - 8
            # print("BLIZU LINIJE, SMANJUJEMO REZULTAT")
        else:
            Globals.lineHitCounter = 0
            # signal.signal(lineHitCounter)

        return masked_image

    def lineDetector(frame):

        frame_g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_blurred = cv2.GaussianBlur(frame_g, (7, 7), 0)

        threshold_low = 10
        threshold_high = 100

        canny = cv2.Canny(frame_blurred, threshold_low, threshold_high)

        # vertices = np.array([[(10,400),(340, 250), (460, 250), (740,400)]], dtype=np.int32)
        # vertices = np.array([[(430,510),(500, 450), (650, 450), (750,510)]], dtype=np.int32)
        vertices = np.array([[(350, 640), (460, 600), (720, 600), (830, 640)]], dtype=np.int32)
        mask = np.zeros_like(frame_g)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(canny, mask)

        rho = 2  # distanca u pikselima
        theta = np.pi / 180  # ugao u radijanima
        threshold = 40  # min broj glasova
        min_line_len = 10  # min broj piksela za liniju
        max_line_gap = 80  # maksimalni razmak izmedju linija
        lines = cv2.HoughLinesP(masked_image, rho, theta, threshold, np.array([]), minLineLength=min_line_len,
                                maxLineGap=max_line_gap)

        # crna slika
        line_image = np.zeros((masked_image.shape[0], masked_image.shape[1], 3), dtype=np.uint8)

        if lines is not None:
            for line in lines:
                if line is not None:
                    for x1, y1, x2, y2 in line:
                        cv2.line(line_image, (x1, y1), (x2, y2), [255, 0, 0], 20)

        mask1 = lineHit(line_image)
        suma = np.sum(mask1)

        # TODO - Create new threads for pedestrian and sign detection

        # Detekcija stop znaka

        StopSignThread(stop_tracker, frame, Globals.previous).start()

        # Detekcija pesaka kod zebre
        # 505000
        if suma > 25000:
            PedestrianThread(pedestrian_tracker, frame).start()

        return line_image

    ref_image = cv2.imread("assets/refimage1.png")
    ref_image_car_width = detectCarInImg(ref_image)

    focal_length_found = focalLength(know_distance, know_width, ref_image_car_width)
    foc = focal_length_found[0][0][0]

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

    while stream.more():

        frame = stream.read()

        Globals.result = Globals.result + 25

        line_frame = lineDetector(frame)
        carDetection = detectCars(frame)

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
                    result = result - 15
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
            db.insert(result)
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
