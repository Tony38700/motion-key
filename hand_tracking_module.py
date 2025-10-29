import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, mode=False, max_hands=2, detection_confidence=0.5,
                 tracking_confidence=0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.results = None
        self.landmark_list = []

        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        self.finger_tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, image, draw=True):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)

        if self.results and self.results.multi_hand_landmarks:
            if self.results.multi_handedness:
                handedness = self.results.multi_handedness[0]
                self.detection_confidence = handedness.classification[0].score * 100

            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(
                        image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return image

    def find_position(self, image, hand_index=0, draw=True):
        x_coords = []
        y_coords = []
        bounding_box = []
        self.landmark_list = []

        if self.results and self.results.multi_hand_landmarks:
            selected_hand = self.results.multi_hand_landmarks[hand_index]

            for landmark_index, landmark in enumerate(selected_hand.landmark):
                height, width, _ = image.shape
                pixel_x, pixel_y = int(landmark.x * width), int(landmark.y * height)
                x_coords.append(pixel_x)
                y_coords.append(pixel_y)
                self.landmark_list.append([landmark_index, pixel_x, pixel_y])

                if draw:
                    cv2.circle(image, (pixel_x, pixel_y), 5, (255, 0, 255), cv2.FILLED)

            if x_coords and y_coords:
                min_x, max_x = min(x_coords), max(x_coords)
                min_y, max_y = min(y_coords), max(y_coords)
                bounding_box = [min_x, min_y, max_x, max_y]

                if draw:
                    cv2.rectangle(image, (min_x - 20, min_y - 20), (max_x + 20, max_y + 20),
                                  (0, 255, 0), 2)

        return self.landmark_list, bounding_box

    @staticmethod
    def get_distance(point1, point2):
        coord_x_1 = int(point1[1])
        coord_y_1 = int(point1[2])
        coord_x_2 = int(point2[1])
        coord_y_2 = int(point2[2])
        return math.hypot(coord_x_2 - coord_x_1, coord_y_2 - coord_y_1)

    @staticmethod
    def draw_distance(point1, point2, image, draw=True, radius=15, thickness=3):
        coord_x_1 = int(point1[1])
        coord_y_1 = int(point1[2])
        coord_x_2 = int(point2[1])
        coord_y_2 = int(point2[2])
        center_x, center_y = (coord_x_1 + coord_x_2) // 2, (coord_y_1 + coord_y_2) // 2

        if draw:
            cv2.line(image, (coord_x_1, coord_y_1), (coord_x_2, coord_y_2),
                     (255, 0, 255), thickness)
            cv2.circle(image, (coord_x_1, coord_y_1), radius, (255, 0, 255), cv2.FILLED)
            cv2.circle(image, (coord_x_2, coord_y_2), radius, (255, 0, 255), cv2.FILLED)
            cv2.circle(image, (center_x, center_y), radius, (0, 0, 255), cv2.FILLED)

        return image, [coord_x_1, coord_x_2, coord_y_1, coord_y_2, center_x, center_y]

    @staticmethod
    def check_fingers_up(landmarks_list):
        if not landmarks_list or len(landmarks_list) < 21:
            return [0, 0, 0, 0, 0]

        fingers = [0, 0, 0, 0, 0]

        reference_points = [
            (4, 3, 2, 'x'),  # Polegar
            (8, 6, 7, 'y'),  # Indicador
            (12, 10, 11, 'y'),  # Médio
            (16, 14, 15, 'y'),  # Anelar
            (20, 18, 19, 'y')  # Mínimo
        ]

        for i, (tip, joint1, joint2, axis) in enumerate(reference_points):
            if i == 0:  # Polegar
                #polegar levantado quando está à ESQUERDA da junta
                if landmarks_list[tip][1] < landmarks_list[joint1][1]:
                    fingers[0] = 1
            else:  # Outros dedos
                if landmarks_list[tip][2] < landmarks_list[joint1][2]:
                    fingers[i] = 1

        return fingers

    @staticmethod
    def check_exit_gesture(fingers):
        return (fingers[0] == 1 and
                all(d == 0 for d in fingers[1:]))

    @staticmethod
    def check_double_click(fingers):
        return all(d == 0 for d in fingers)

    @staticmethod
    def check_scroll_up(fingers):
        return (fingers[0] == 1 and fingers[1] == 1 and
                all(d == 0 for d in fingers[2:]))

    @staticmethod
    def check_scroll_down(fingers):
        return (fingers[0] == 1 and fingers[4] == 1 and
                all(d == 0 for d in fingers[1:4]))
