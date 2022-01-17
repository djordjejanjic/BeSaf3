def focalLength(measured_distance, real_width, width_in_rf_image):
    focal_length = (width_in_rf_image * measured_distance) / real_width
    return focal_length


def distanceFinder(focal_length, real_car_width, car_width_in_frame):
    distance = (real_car_width * focal_length) / car_width_in_frame
    return distance
