import cv2


class Globals:
    path = 'assets/test-vozilo.mp4'
    imagePath = 'assets/refimage1.png'

    lineHitCounter = 0
    result = 0
    car_width_global = 0
    signal = 0
    previous = None

    classifierCars = 'models/cars.xml'
    classifierPedestrian = 'models/pedestrian.xml'
    classifierStopSign = 'models/stopsign_classifier.xml'

    fonts = cv2.FONT_HERSHEY_COMPLEX

    # Detektuje samo automobile isped i meri distancu
    previous_distance = 0
    safe_distance = 800
    know_distance = 800  # centimetri
    know_width = 150

    pedestrianRectangle = []
    carRectangle = []
    stopSignRectangle = []
