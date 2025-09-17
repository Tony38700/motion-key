import cv2
import numpy as np
import time
import autopy
from hand_tracking_module import HandDetector

# Configurações/constantes
CAM_WIDTH, CAM_HEIGHT = 640, 480  # resolução da câmera
FRAME_REDUCTION = 100  # redução de frame
SMOOTHENING = 7  # suavização do movimento dos dedos

# Webcam
camera = cv2.VideoCapture(0)  # 0 - câmera padrão; 1 - câmera externa
camera.set(3, CAM_WIDTH)  # largura
camera.set(4, CAM_HEIGHT)  # altura

# Tempo e detecção
prev_time = 0  # variável tempo do FPS
hand_detector = HandDetector(MAX_HANDS=1)  # uma mão por vez

# Tela
screen_width, screen_height = autopy.screen.size()  # capturar a resolução da tela
prev_cursor_x, prev_cursor_y = 0, 0  # posição anterior do cursor (suavização)
curr_cursor_x, curr_cursor_y = 0, 0  # posição atual do cursor (suavização)

# Verifica se a câmera abriu corretamente
if not camera.isOpened():
    print("Não foi possível abrir a câmera.")
    exit()

while True:
    # 1. Encontrar pontos de referência para as mãos
    success, frame = camera.read()  # captura frame da webcam
    frame = hand_detector.find_hands(frame)  # chama classe HandDetector
    landmarks_list, bounding_box = hand_detector.find_position(frame)  # parametro da img

    # 2. Pegar a ponta dos dedos indicador(1) e médio(2)
    index_x = index_y = middle_x = middle_y = 0  # variáveis
    if len(landmarks_list) != 0:
        index_x, index_y = landmarks_list[8][1:]  # ponto 8
        middle_x, middle_y = landmarks_list[12][1:]  # ponto 12

    # 3. Verificar quais dedos estão levantados
    fingers = hand_detector.fingers_up()
    cv2.rectangle(frame, (FRAME_REDUCTION, FRAME_REDUCTION), (CAM_WIDTH - FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION),
                  (255, 0, 255), 2)  # limitação do mouse na webcam

    # Método de confiança
    if hasattr(hand_detector, 'detection_confidence') and hand_detector.detection_confidence > 0:
        conf_text = f"Confianca: {hand_detector.detection_confidence:.1f}%"
        cv2.putText(frame, conf_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)

    # 4. Apenas dedo indicador: modo de movimento
    if fingers[1] == 1 and fingers[2] == 0:
        # Converter coordenadas da webcam para o monitor
        mapped_x = np.interp(index_x, (FRAME_REDUCTION, CAM_WIDTH - FRAME_REDUCTION), (0, screen_width))
        mapped_y = np.interp(index_y, (FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION), (0, screen_height))
        # Suavizar valores
        curr_cursor_x = prev_cursor_x + (mapped_x - prev_cursor_x) / SMOOTHENING
        curr_cursor_y = prev_cursor_y + (mapped_y - prev_cursor_y) / SMOOTHENING
        # Mover o mouse (inverte eixo X para movimento espelhado)
        autopy.mouse.move(screen_width - curr_cursor_x, curr_cursor_y)
        cv2.circle(frame, (index_x, index_y), 15, (255, 0, 255), cv2.FILLED)  # marcar mouse em roxo
        prev_cursor_x, prev_cursor_y = curr_cursor_x, curr_cursor_y

    # 5. Se dedo indicador e médio estiverem levantados: Modo de clique
    if fingers[1] == 1 and fingers[2] == 1:
        # Encontrar a distância entre os dedos
        distance, frame, line_info = hand_detector.find_distance(8, 12, frame)
        print(distance)
        # Clicar com o mouse se a distância for curta
        if distance < 40:
            cv2.circle(frame, (line_info[4], line_info[5]),
                       15, (0, 255, 0), cv2.FILLED)  # confirmar click com circulo verde
            autopy.mouse.click()

    # 6. FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)  # calcula FPS
    prev_time = curr_time
    cv2.putText(frame, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)

    # Display
    cv2.imshow('Image', frame)  # cria janela
    # Pressione 'esc' para sair do loop
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Libera recursos após sair do loop
camera.release()
cv2.destroyAllWindows()
