import cv2


class Globals:
    path = 'assets/bg-video-2022-22.mp4'
    imagePath = 'assets/refimage1.png'

    lineHitCounter = 0
    result = 0
    car_width_global = 0
    signal = 0
    previous = None

    classifierCars = 'models/cars.xml'
    classifierPedestrian = 'models/pedestrian.xml'
    classifierStopSign = 'models/stopsign_classifier.xml'

    fonts = cv2.FONT_HERSHEY_SIMPLEX

    # Detektuje samo automobile isped i meri distancu
    previous_distance = 0
    safe_distance = 800
    know_distance = 800  # centimetri
    know_width = 150
