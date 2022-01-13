import time
# import signal as signal
import cv2
import numpy as np
import operations
from threading import Thread
from streamthread import FileVideoStream
from pedestriandetectionthread import PedestrianDetection
import time
from matplotlib import pyplot as plt

lineHitCounter = 0
result = 0
car_width_global = 0
signal = 0
previous = None

stream = FileVideoStream('assets/test-vozilo.mp4').start()
ped = PedestrianDetection()

def startVideo():
    # cap = cv2.VideoCapture('stop_test.mp4')
    # cap = cv2.VideoCapture('videodriving.mp4')

    # cap = cv2.VideoCapture('pedestrian_test.mp4')

    classifier = 'models/cars.xml'

    classifierPedestrian = 'models/pedestrian.xml'

    stopSignClassifier = 'models/stopsign_classifier.xml'

    car_tracker = cv2.CascadeClassifier(classifier)
    pedestrian_tracker = cv2.CascadeClassifier(classifierPedestrian)
    stop_tracker = cv2.CascadeClassifier(stopSignClassifier)

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

        car_width = 0
        frame_g = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # maskiranje
        # vertices = np.array([[(550,600),(550, 300), (750, 300), (750,600)]], dtype=np.int32)
        vertices = np.array([[(520, 600), (550, 330), (750, 330), (780, 600)]], dtype=np.int32)
        mask = np.zeros_like(frame_g)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(frame_g, mask)

        cars = car_tracker.detectMultiScale(masked_image, minSize=(50, 50))

        global car_width_global
        for (x, y, w, h) in cars:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # print("ww",w)

            car_width_global = w

            # print("cwg",car_width_global)

        return frame

    def detectCars1(img):

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

        global lineHitCounter
        global result
        if np.sum(masked_image) != 0:
            lineHitCounter = 1
            # signal.signal(lineHitCounter)
            result = result - 8
            print("BLIZU LINIJE, SMANJUJEMO REZULTAT")
        else:
            lineHitCounter = 0
            # signal.signal(lineHitCounter)
        print(lineHitCounter)

        return masked_image

    def stop(frame_g, frame):

        vertices = np.array([[(860, 550), (860, 140), (1200, 140), (1200, 550)]], dtype=np.int32)
        mask = np.zeros_like(frame_g)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(frame_g, mask)
        stop = stop_tracker.detectMultiScale(masked_image)
        # cv2.imshow("znaktest", masked_image)

        vertices_stop = np.array([[(860, 400), (860, 140), (1200, 140), (1200, 400)]], dtype=np.int32)
        mask_stop = np.zeros_like(frame_g)
        cv2.fillPoly(mask_stop, vertices_stop, 255)
        masked_image_stop = cv2.bitwise_and(frame_g, mask_stop)
        if stop is not None:
            for (x, y, w, h) in stop:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 255), 2)
                # signal.signal(1)
                print("ZNAK STOP")
                global previous
                if previous is not None:
                    diff = cv2.absdiff(previous, masked_image_stop)
                    # cv2.imshow("diff", diff)
                    if np.sum(diff) != 0:
                        print("STOP!!!")
                        # signal.signal(1)
                    else:
                        print("DRIVER HAS STOPPED!")
                previous = masked_image_stop
        # else:
        # signal.signal(0)

    def pedestrians(frame_g, frame):
        print("YOU CROSSED THE ZEBRA CROSSING")
        vertices = np.array([[(50, 720), (50, 300), (1200, 300), (1200, 720)]], dtype=np.int32)
        mask = np.zeros_like(frame_g)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(frame_g, mask)
        # cv2.imshow("pesak", masked_image)
        pedestrians = pedestrian_tracker.detectMultiScale(masked_image)
        if pedestrians is not None:
            for (x, y, w, h) in pedestrians:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                if pedestrians is not None:
                    print("PEDESTRIAN NEAR ZEBRA CROSSING!!!")
                    # signal.signal(1)
                # else:
                # signal.signal(0)

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
        print(suma)

        # TODO - Create new threads for pedestrian and sign detection

        # Detekcija stop znaka

        # stop(frame_g, frame)

        # Detekcija pesaka kod zebre
        # 505000
        # if(suma > 1000):
        #     pedestrians(frame_g, frame)

        # ped.pedestrians(pedestrian_tracker, frame_g, frame)


        return line_image

    ref_image = cv2.imread("assets/refimage1.png")

    ref_image_car_width = detectCars1(ref_image)

    # cv2.imshow("test",ref_image_car_width)

    focal_length_found = focalLength(know_distance, know_width, ref_image_car_width)
    # print(focal_length_found[0][0][0])
    foc = focal_length_found[0][0][0]

    # print("FOCAL", foc)

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

        global result
        result = result + 25

        print(result)

        line_frame = lineDetector(frame)
        # lineDetector(frame)
        # carDetector
        carDetection = detectCars(frame)
        # cv2.imshow("CAR D", carDetection)
        carDetectionWidth = car_width_global

        # print("CAR D WIDTH",carDetectionWidth)
        # overlay = apply_color(carDetection, 0, 0, 0, 0)
        cv2.putText(carDetection, f"Result: {result}", (800, 50), fonts, 1.2, (0, 0, 255), 2)
        if carDetectionWidth != 0:

            Distance = distanceFinder(foc, know_width, carDetectionWidth)
            DistanceInCM = round(Distance)
            cv2.putText(carDetection, f"Distance: {DistanceInCM} cm", (50, 50), fonts, 0.6, (255, 255, 255), 2)

            print("distance", DistanceInCM)
            if (Distance < safe_distance):
                if (previous_distance != Distance):
                    previous_distance = Distance
                    cv2.putText(carDetection, "WARNING! SLOW DOWN!", (400, 650), fonts, 1.2, (0, 0, 255), 2)
                    blue = 230
                    intensity = 0.3
                    result = result - 15
                    # print("BLIZU KOLA, SMANJUJEMO REZULTAT")
                    carDetection = apply_color(carDetection, intensity, blue, 0, 0)
        else:
            cv2.putText(carDetection, f"Not available", (50, 50), fonts, 0.6, (255, 255, 255), 2)

        image_whole = cv2.addWeighted(carDetection, 1, line_frame, 1, 0)
        # formatiraj za prikaz u pretrazivacu
        imgencode = cv2.imencode('.jpg', image_whole)[1]
        strinData = imgencode.tostring()
        yield (b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n' + strinData + b'\r\n')

        # cv2.imshow('car_detection', carDetection)

        # cv2.imshow('line_frame', line_frame)

        print("SIGNAL ", signal)
        # global signal
        if (signal == 1):
            # operations.insert(result)
            break

        k = cv2.waitKey(30) & 0xff
        if k == 27:
            operations.insert(result)
            break

        stream.stop()
        cv2.destroyAllWindows()


def stopAndSave():
    operations.insert(result)
    print("STOPIRANO")
    global signal
    signal = 1
    stream.stop()
    cv2.destroyAllWindows()


def restart():
    global signal
    signal = 0
