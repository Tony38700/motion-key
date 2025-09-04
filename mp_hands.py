import cv2
import mediapipe as mp
import pyautogui
import math

# DESATIVAR APENAS SE NÃO FOR CRÍTICO
pyautogui.FAILSAFE = False

SENSIBILIDADE_DO_MODELO = 2.0

cam = cv2.VideoCapture(0)
hands = mp.solutions.hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
mp_draw = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()

# Calcula distância euclidiana entre dois landmarks normalizados
def distancia(ponto_1, ponto_2, width, height):
    coord_x_1 = int(ponto_1.x * width)
    coord_y_1 = int(ponto_1.y * height)
    coord_x_2 = int(ponto_2.x * width)
    coord_y_2 = int(ponto_2.y * height)
    return math.hypot(coord_x_2 - coord_x_1, coord_y_2 - coord_y_1)

# Retorna True se os 4 dedos (exceto polegar) estiverem levantados
def mao_aberta(landmarks):
    dedos = [(8, 6), (12, 10), (16, 14), (20, 18)]
    return all(landmarks[tip].y < landmarks[base].y for tip, base in dedos)

# Retorna True se a distância entre o indicador e a base for maior ou igual à distância usada para avaliar o punho fechado
def indicador_unico_levantado(landmarks, threshold=160):
    return distancia(landmarks[8], landmarks[5], screen_width, screen_height) >= threshold

# Retorna True se o topo dos 4 dedos (sem contar o polegar) estiver proximo à junta da mão com os dedos
def punho_fechado(landmarks, threshold=160):
    dedos = [(8, 5), (12, 9), (16, 13), (20, 17)]
    return all(distancia(landmarks[tip], landmarks[base], screen_width, screen_height) < threshold for tip, base in dedos)

# Retorna True se o polegar e o indicador estiverem encostados (para arrastar)
def polegar_indicador_encostados(landmarks, img_width, img_height, threshold=40):
    polegar = landmarks[4]
    indicador = landmarks[8]
    dist = distancia(polegar, indicador, img_width, img_height)
    return dist < threshold

drag_ativo = False

while True:
    _, img = cam.read()
    img = cv2.flip(img, 1)  # espelha a imagem
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    results = hands.process(rgb_frame)
    landmark_points = results.multi_hand_landmarks

    if landmark_points:
        hand_landmarks = landmark_points[0]
        mp_draw.draw_landmarks(img, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
        landmarks = hand_landmarks.landmark
        img_height, img_width, _ = img.shape

        polegar = landmarks[4]
        indicador = landmarks[8]

        if punho_fechado(landmarks):
            cv2.putText(img, "Neutro", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (128, 128, 128), 3)
            if drag_ativo:
                pyautogui.mouseUp()
                drag_ativo = False
            pass

        elif polegar_indicador_encostados(landmarks, img_width, img_height):
            x = int(indicador.x * img_width)
            y = int(indicador.y * img_height)
            cv2.circle(img, (x, y), 12, (255, 0, 0), cv2.FILLED)

            # Converte para coordenadas de tela
            screen_x = int(screen_width * (indicador.x - 0.3) * SENSIBILIDADE_DO_MODELO)
            screen_y = int(screen_height * (indicador.y - 0.3) * SENSIBILIDADE_DO_MODELO)
            screen_x = max(0, min(screen_width - 1, screen_x))
            screen_y = max(0, min(screen_height - 1, screen_y))
            pyautogui.moveTo(screen_x, screen_y)

            # Inicia o clique e segurar
            if not drag_ativo:
                pyautogui.mouseDown()
                drag_ativo = True

        else:
            # Solta o mouse se estava arrastando
            if drag_ativo:
                pyautogui.mouseUp()
                drag_ativo = False

        if mao_aberta(landmarks):
            cv2.putText(img, "Clique!", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            pyautogui.click()
            pyautogui.sleep(1)
            if drag_ativo:
                pyautogui.mouseUp()
                drag_ativo = False

        elif indicador_unico_levantado(landmarks):
            x = int(indicador.x * img_width)
            y = int(indicador.y * img_height)
            cv2.circle(img, (x, y), 12, (0, 255, 0), cv2.FILLED)

            screen_x = int(screen_width * (indicador.x - 0.3) * SENSIBILIDADE_DO_MODELO)
            screen_y = int(screen_height * (indicador.y - 0.3) * SENSIBILIDADE_DO_MODELO)
            screen_x = max(0, min(screen_width - 1, screen_x))
            screen_y = max(0, min(screen_height - 1, screen_y))
            pyautogui.moveTo(screen_x, screen_y)

    cv2.imshow('Hand Controlled Mouse', img)

    # Apertar a tecla 'q' para encerrar
    if cv2.waitKey(20) & 0xFF == ord('q'):
        break

# Liberar recursos
cam.release()
cv2.destroyAllWindows()
