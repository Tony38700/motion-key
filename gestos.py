import cv2
import mediapipe as mp
import pyautogui

# Inicializa MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Função simples para classificar 3 gestos
def classificar_gesto(landmarks):
    # Coordenadas dos dedos (y)
    y_polegar = landmarks[mp_hands.HandLandmark.THUMB_TIP].y
    y_indicador = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
    y_medio = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y
    y_anelar = landmarks[mp_hands.HandLandmark.RING_FINGER_TIP].y
    y_mindinho = landmarks[mp_hands.HandLandmark.PINKY_TIP].y
    # Ponto central da palma: usa o ponto MIDDLE_FINGER_MCP
    y_palma = landmarks[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y

    margem = 0.08  # tolerância maior para facilitar reconhecimento

    # Só considera indicador, médio e anelar
    dedos = [y_indicador, y_medio, y_anelar]
    acima = [d < y_palma - margem for d in dedos]

    # 1 dedo: só o indicador levantado
    if acima[0] and not any(acima[1:]):
        return "1"
    # 2 dedos: indicador e médio levantados
    if acima[0] and acima[1] and not acima[2]:
        return "2"
    # 3 dedos: indicador, médio e anelar levantados
    if acima[0] and acima[1] and acima[2]:
        return "3"

    return None

# Acessar a câmera (ajuste o índice caso não abra, ex: 0, 1, 2...)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Variável global para controle do gesto anterior
gesto_anterior = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Converte para RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultado = hands.process(frame_rgb)


    gesto = None
    if resultado.multi_hand_landmarks:
        for hand_landmarks in resultado.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesto = classificar_gesto(hand_landmarks.landmark)

    # Controle de gesto anterior para evitar prints repetidos
    if gesto and gesto != gesto_anterior:
        print(f"Gesto detectado: {gesto}")
        gesto_anterior = gesto

    # Mostrar mensagem na tela
    if gesto:
        cv2.putText(frame, f"Gesto: {gesto}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
    else:
        cv2.putText(frame, "Nenhum gesto", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    # Exibir vídeo
    cv2.imshow("Reconhecimento de Gestos", frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
