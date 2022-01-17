import numpy as np
import cv2
from globals.globals import Globals


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

    # Detekcija stop znaka

    # StopSignThread(stop_tracker, frame, Globals.previous).start()

    # Detekcija pesaka kod zebre
    # 505000
    # if suma > 25000:
    #     PedestrianThread(pedestrian_tracker, frame).start()

    return line_image
