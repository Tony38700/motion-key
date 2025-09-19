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

        self.hands = mp.solutions.hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        # IDs dos dedos: polegar, indicador, médio, anelar e mindinho
        self.finger_tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, image, draw=True):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(image_rgb)

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

    def get_distance(self, point1, point2):
        coord_x_1 = int(point1[1])
        coord_y_1 = int(point1[2])
        coord_x_2 = int(point2[1])
        coord_y_2 = int(point2[2])
        return math.hypot(coord_x_2 - coord_x_1, coord_y_2 - coord_y_1)

    def draw_distance(self, point1, point2, image, draw=True, radius=15, thickness=3):
        coord_x_1 = int(point1[1])
        coord_y_1 = int(point1[2])
        coord_x_2 = int(point2[1])
        coord_y_2 = int(point2[2])
        center_x, center_y = (coord_x_1 + coord_x_2) // 2, (coord_y_1 + coord_y_2) // 2

        # círculos e linha
        if draw:
            cv2.line(image, (coord_x_1, coord_y_1), (coord_x_2, coord_y_2),
                     (255, 0, 255), thickness)  # entre pontos
            cv2.circle(image, (coord_x_1, coord_y_1), radius, (255, 0, 255), cv2.FILLED)  # no ponto 1
            cv2.circle(image, (coord_x_2, coord_y_2), radius, (255, 0, 255), cv2.FILLED)  # no ponto 2
            cv2.circle(image, (center_x, center_y), radius, (0, 0, 255), cv2.FILLED)  # central

        return image, [coord_x_1, coord_x_2, coord_y_1, coord_y_2, center_x, center_y]


# Funções auxiliares para gestos
def verificar_dedos_levantados(landmarks_list):
    """Verifica quais dedos estão levantados com base nos landmarks."""
    dedos = [0, 0, 0, 0, 0]  # [polegar, indicador, medio, anelar, minimo]

    # Pontas dos dedos e suas juntas de referência
    pontos_referencia = [
        (4, 3, 2, 'x'),  # Polegar (usa coordenada x)
        (8, 6, 7, 'y'),  # Indicador
        (12, 10, 11, 'y'),  # Médio
        (16, 14, 15, 'y'),  # Anelar
        (20, 18, 19, 'y')  # Mínimo
    ]

    for i, (ponta, junta1, junta2, eixo) in enumerate(pontos_referencia):
        if i == 0:  # Polegar (lógica especial)
            if landmarks_list[ponta][1] > landmarks_list[junta1][1]:
                dedos[0] = 1
        else:  # Outros dedos
            if landmarks_list[ponta][2] < landmarks_list[junta1][2]:
                dedos[i] = 1

    return dedos


def verificar_gesto_saida(dedos):
    """Verifica gesto de saída: polegar levantado + outros dedos abaixados."""
    return (dedos[0] == 1 and  # Polegar levantado
            all(d == 0 for d in dedos[1:]))  # Todos os outros dedos abaixados


def verificar_clique_duplo(dedos):
    """Verifica gesto de clique duplo: todos dedos abaixados."""
    return all(d == 0 for d in dedos)
