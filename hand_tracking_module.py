import cv2
import mediapipe as mp
import math

class HandDetector:
    def __init__(self, MODE=False, MAX_HANDS=2, DETECTION_CONFIDENCE=0.5, TRACKING_CONFIDENCE=0.5):
        self.MODE = MODE
        self.MAX_HANDS = MAX_HANDS
        self.DETECTION_CONFIDENCE = DETECTION_CONFIDENCE
        self.TRACKING_CONFIDENCE = TRACKING_CONFIDENCE

        self.hands = mp.solutions.hands.Hands(
            static_image_mode=self.MODE,
            max_num_hands=self.MAX_HANDS,
            min_detection_confidence=self.DETECTION_CONFIDENCE,
            min_tracking_confidence=self.TRACKING_CONFIDENCE
        )
        # IDs dos dedos: polegar, indicador, médio, anelar e mindinho
        self.FINGER_TIP_IDS = [4, 8, 12, 16, 20]

    def find_hands(self, image, draw=True):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)
        self.detection_confidence = 0.0

        # desenha landmarks nas mãos
        if self.results.multi_hand_landmarks:
            if self.results.multi_handedness:
                handedness = self.results.multi_handedness[0]
                self.detection_confidence = handedness.classification[0].score * 100

            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    mp.solutions.drawing_utils.draw_landmarks(
                        image, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)

        return image

    def find_position(self, image, hand_index=0, draw=True):
        x_coords = []
        y_coords = []
        bounding_box = []
        self.landmark_list = []
        if self.results.multi_hand_landmarks:
            # preferência para primeira mão
            selected_hand = self.results.multi_hand_landmarks[hand_index]

            # coordenadas para pixel
            for landmark_index, landmark in enumerate(selected_hand.landmark):
                height, width, _ = image.shape
                pixel_x, pixel_y = int(landmark.x * width), int(landmark.y * height)
                x_coords.append(pixel_x)
                y_coords.append(pixel_y)
                self.landmark_list.append([landmark_index, pixel_x, pixel_y])  # armazena ID, coordenadas xy
                if draw:
                    cv2.circle(image, (pixel_x, pixel_y), 5, (255, 0, 255), cv2.FILLED)

            min_x, max_x = min(x_coords), max(x_coords)
            min_y, max_y = min(y_coords), max(y_coords)
            bounding_box = min_x, min_y, max_x, max_y

            if draw:
                cv2.rectangle(image, (min_x - 20, min_y - 20), (max_x + 20, max_y + 20),
                              (0, 255, 0), 2)

        return self.landmark_list, bounding_box

    def fingers_up(self):
        fingers_status = []
        if not hasattr(self, 'landmark_list') or len(self.landmark_list) == 0:
            # retorna todos os dedos abaixados se não detectar mão
            return [0, 0, 0, 0, 0]

        # Polegar
        if self.landmark_list[self.FINGER_TIP_IDS[0]][1] < self.landmark_list[self.FINGER_TIP_IDS[0] - 1][1]:
            fingers_status.append(1)  # polegar aberto
        else:
            fingers_status.append(0)  # polegar fechado

        # Outros dedos
        for finger_index in range(1, 5):
            if self.landmark_list[self.FINGER_TIP_IDS[finger_index]][2] < self.landmark_list[self.FINGER_TIP_IDS[finger_index] - 2][2]:
                fingers_status.append(1)  # dedo levantado
            else:
                fingers_status.append(0)  # dedo abaixado

        # lista de dedos levantados ou não
        return fingers_status

    def find_distance(self, point1_index, point2_index, image, draw=True, radius=15, thickness=3):
        point1_x, point1_y = self.landmark_list[point1_index][1:]  # coordenadas do ponto 1
        point2_x, point2_y = self.landmark_list[point2_index][1:]  # coordenadas do ponto 2
        center_x, center_y = (point1_x + point2_x) // 2, (point1_y + point2_y) // 2  # centro entre os pontos

        # círculos e linha
        if draw:
            cv2.line(image, (point1_x, point1_y), (point2_x, point2_y), (255, 0, 255), thickness)  # entre pontos
            cv2.circle(image, (point1_x, point1_y), radius, (255, 0, 255), cv2.FILLED)  # no ponto 1
            cv2.circle(image, (point2_x, point2_y), radius, (255, 0, 255), cv2.FILLED)  # no ponto 2
            cv2.circle(image, (center_x, center_y), radius, (0, 0, 255), cv2.FILLED)  # central
        distance = math.hypot(point2_x - point1_x, point2_y - point1_y)  # distância média entre os pontos

        return distance, image, [point1_x, point1_y, point2_x, point2_y, center_x, center_y]
