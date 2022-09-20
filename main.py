import cv2
import numpy as np

from globals.globals import Globals
from utility.static_car_detection import StaticCarDetection
from utility.effects import apply_color
from utility.line_detection import lineDetector
from utility.focal_length import focalLength, distanceFinder
from threads.streamthread import FileVideoStream
from threads.car_detection import CarThread
from threads.pedestrian_detection import PedestrianThread
from threads.stop_sign_detection import StopSignThread

# from signal import signal

stream = FileVideoStream(Globals.path).start()

net = cv2.dnn.readNet('yolov3-tiny_final.weights', 'yolov3.cfg')
classes = []
with open("coco.names", "r") as f:
    classes = f.read().splitlines()

# cap = cv2.VideoCapture('test1.mp4')
font = cv2.FONT_HERSHEY_PLAIN

def startVideo(db):
    car_tracker = cv2.CascadeClassifier(Globals.classifierCars)
    # pedestrian_tracker = cv2.CascadeClassifier(Globals.classifierPedestrian)
    # stop_tracker = cv2.CascadeClassifier(Globals.classifierStopSign)
    #
    ref_image = cv2.imread(Globals.imagePath)
    ref_image_car_width = StaticCarDetection().detectCarInImg(ref_image, car_tracker)
    #
    focal_length_found = focalLength(Globals.know_distance, Globals.know_width, ref_image_car_width)
    foc = focal_length_found[0][0][0]

    while stream.more():

        frame = stream.read()

        vertices = np.array([[(520, 600), (550, 330), (750, 330), (780, 600)]], dtype=np.int32)
        mask = np.zeros_like(frame)
        cv2.fillPoly(mask, vertices, 255)
        masked_image = cv2.bitwise_and(frame, mask)
        height, width, _ = frame.shape

        Globals.result = Globals.result + 25
        line_frame = lineDetector(frame)

        carDet = CarThread(car_tracker, frame)
        carDetection = carDet.detectCars()
        # StopSignThread(stop_tracker, frame, Globals.previous).start()
        # PedestrianThread(pedestrian_tracker, frame).start()

        carDetectionWidth = Globals.car_width_global

        blob = cv2.dnn.blobFromImage(frame, 1 / 255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
        net.setInput(blob)
        output_layers_names = net.getUnconnectedOutLayersNames()
        layerOutputs = net.forward(output_layers_names)

        boxes = []
        confidences = []
        class_ids = []

        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.7:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.2, 0.4)

        if len(indexes) > 0:
            for i in indexes.flatten():
                x, y, w, h = boxes[i]
                color = (0, 0, 139)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)

        cv2.putText(frame, f"Result: {Globals.result}", (800, 50), Globals.fonts, 1.2, (0, 0, 255), 2)
        if carDetectionWidth != 0:

            Distance = distanceFinder(foc, Globals.know_width, carDetectionWidth)
            DistanceInCM = round(Distance)
            cv2.putText(frame, f"Distance: {DistanceInCM} cm", (50, 50), Globals.fonts, 0.6, (255, 255, 255), 2)

            if Distance < Globals.safe_distance:

                if Globals.previous_distance != Distance:
                    Globals.previous_distance = Distance
                    cv2.putText(frame, "WARNING! SLOW DOWN!", (400, 650), Globals.fonts, 1.2, (0, 0, 255), 2)
                    intensity = 0.3
                    Globals.result = Globals.result - 15
                    frame = apply_color(frame, intensity, 0, 0, 139)
        else:
            cv2.putText(frame, f"Not available", (50, 50), Globals.fonts, 0.6, (255, 255, 255), 2)

        image_whole = cv2.addWeighted(frame, 1, line_frame, 1, 0)

        # formatiraj za prikaz u pretrazivacu
        imgCode = cv2.imencode('.jpg', image_whole)[1]
        stringData = imgCode.tostring()
        yield b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n' + stringData + b'\r\n'

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
