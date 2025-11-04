import cv2
import numpy as np
import time
import autopy
import pyautogui  # Para scroll e minimizar telas
from hand_tracking_module_esq import HandDetector
from gesture_logger import GestureLogger
from calculation_logger import CalculationLogger
from async_logger import AsyncLogger
import os

"""""""""
Movimento: Polegar + Indicador + Médio levantados ✌️
Arrasto: Polegar abaixado + Indicador tocando no polegar + outros 3 levantados 👌 
Clique Esquerdo: Médio levantado + outros abaixados 🖱️🖕
Clique Direito: Indicador levantado + outros abaixados 👆🖱️
Clique Duplo: Todos os dedos abaixados 🖱️👍(-90º)🖱️
Scroll Up: Polegar + Indicador levantados 👆
Scroll Down: Polegar + Mindinho levantados 🤟
Sair: Polegar levantado + outros abaixados (3 segundos) ✊ 
"""""""""

# Configurações/constantes
CAM_WIDTH, CAM_HEIGHT = 640, 480
FRAME_REDUCTION = 100
SMOOTHENING = 7  # Suavização do mouse
SMOOTHENING_DRAG = 7  # Suavização do arrasto
DRAG_DISTANCE_THRESHOLD = 20  # Distância máxima para ativar arrasto
EXIT_GESTURE_TIME = 3.0  # 3 segundos com gesto de saída
DOUBLE_CLICK_COOLDOWN = 2.0  # 2 segundo entre cliques duplos

def main():
    pyautogui.hotkey('win', 'd')
    # 1. inicialização
    camera = cv2.VideoCapture(0)
    camera.set(3, CAM_WIDTH)
    camera.set(4, CAM_HEIGHT)

    # 1.1. Configurações de detecção
    prev_time = 0
    hand_detector = HandDetector(max_hands=1)

    # 1.2. Configurações de tela e movimento
    screen_width, screen_height = autopy.screen.size()
    prev_cursor_x, prev_cursor_y = 0, 0  # Mouse normal
    curr_cursor_x, curr_cursor_y = 0, 0
    prev_drag_x, prev_drag_y = 0, 0  # Arrasto
    curr_drag_x, curr_drag_y = 0, 0

    # 1.3. Conectar as funções
    gesture_logger = GestureLogger()
    uid_env = os.environ.get('USER_ID')
    if uid_env:
        try:
            gesture_logger.user_id = int(uid_env)
        except Exception:
            gesture_logger.user_id = None
    gesture_logger.hand_used = 'left'
    calculation_logger = CalculationLogger()
    async_logger = AsyncLogger(gesture_logger, calculation_logger, batch_interval=5.0)  # 5 segundos

    # 2. Estados das variáveis
    mouse_locked = False
    drag_active = False
    last_click = 0
    last_double_click = 0
    last_scroll = 0
    clique_cooldown = 1.0
    scroll_cooldown = 0.5
    exit_gesture_start_time = 0
    exit_gesture_active = False
    fingers = [0, 0, 0, 0, 0]

    if not camera.isOpened():
        print("Não foi possível abrir a câmera.")
        return

    while True:
        # 3. Captura e processamento de frames
        success, frame = camera.read()
        if not success:
            continue

        frame = hand_detector.find_hands(frame)
        landmarks_list, bounding_box = hand_detector.find_position(frame)

        # Área útil do mouse
        cv2.rectangle(frame, (FRAME_REDUCTION, FRAME_REDUCTION),
                      (CAM_WIDTH - FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION),
                      (255, 0, 255), 2)

        if landmarks_list:
            # 4. DETECÇÃO DE GESTOS
            fingers = hand_detector.check_fingers_up(landmarks_list)
            thumb_x, thumb_y = landmarks_list[4][1], landmarks_list[4][2]
            index_x, index_y = landmarks_list[8][1], landmarks_list[8][2]
            middle_x, middle_y = landmarks_list[12][1], landmarks_list[12][2]

            confidence = getattr(hand_detector, 'detection_confidence', None)
            async_logger.log_gesture(fingers, landmarks_list, hand_detector, confidence, bounding_box)
            async_logger.log_calculation('log_finger_positions', landmarks_list)
            async_logger.log_calculation('log_hand_geometry', landmarks_list)

            # 5. Metodo de confiança
            if hasattr(hand_detector, 'detection_confidence') and hand_detector.detection_confidence > 0:
                conf_text = f"Confianca: {hand_detector.detection_confidence:.1f}%"
                cv2.putText(frame, conf_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 0), 2)

            # 6. GESTOS PRINCIPAIS
            # 6.1. Clique Duplo
            if hand_detector.check_double_click(fingers) and not drag_active:
                current_time = time.time()
                if current_time - last_double_click > DOUBLE_CLICK_COOLDOWN:
                    try:
                        autopy.mouse.click(autopy.mouse.Button.LEFT)
                        time.sleep(0.1)
                        autopy.mouse.click(autopy.mouse.Button.LEFT)
                        cv2.putText(frame, "CLIQUE DUPLO!", (10, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        last_double_click = current_time
                        print("Clique duplo executado!")
                        async_logger.log_calculation('log_double_click', fingers)
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"Erro no clique duplo: {e}")

            # 6.2. Arrasto
            elif (fingers[0] == 0 and fingers[2] == 1 and
                  fingers[3] == 1 and fingers[4] == 1):
                distancia = hand_detector.get_distance(landmarks_list[4], landmarks_list[8])

                async_logger.log_calculation('log_distance_calculation', landmarks_list[4], landmarks_list[8], distancia)

                if distancia < DRAG_DISTANCE_THRESHOLD:
                    cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 255, 255), cv2.FILLED)
                    cv2.circle(frame, (index_x, index_y), 10, (0, 255, 255), cv2.FILLED)
                    cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 255), 2)
                    cv2.putText(frame, f"Dist: {int(distancia)}", (thumb_x, thumb_y - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                if distancia < DRAG_DISTANCE_THRESHOLD:
                    if not drag_active:
                        autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                        drag_active = True
                        cv2.putText(frame, "ARRASTANDO", (10, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        print("Arrasto ativado")
                        prev_drag_x, prev_drag_y = index_x, index_y

                    cursor_x, cursor_y = index_x, index_y
                    mapped_x = np.interp(cursor_x, (FRAME_REDUCTION, CAM_WIDTH - FRAME_REDUCTION), (0, screen_width))
                    mapped_y = np.interp(cursor_y, (FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION), (0, screen_height))

                    curr_drag_x = prev_drag_x + (mapped_x - prev_drag_x) / SMOOTHENING_DRAG
                    curr_drag_y = prev_drag_y + (mapped_y - prev_drag_y) / SMOOTHENING_DRAG

                    autopy.mouse.move(screen_width - curr_drag_x, curr_drag_y)
                    prev_drag_x, prev_drag_y = curr_drag_x, curr_drag_y
                    cv2.circle(frame, (cursor_x, cursor_y), 12, (255, 0, 255), cv2.FILLED)
                    async_logger.log_calculation('log_drag_operation', fingers, (thumb_x, thumb_y), (index_x, index_y), distancia, drag_active)

                else:
                    if drag_active:
                        autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                        drag_active = False
                        cv2.putText(frame, "ARRASTO LIBERADO", (10, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        print("Arrasto desativado")

            # 6.3. Scroll Up
            elif hand_detector.check_scroll_up(fingers) and not drag_active:
                current_time = time.time()
                if current_time - last_scroll > scroll_cooldown:
                    try:
                        pyautogui.scroll(200)
                        cv2.putText(frame, "SCROLL UP", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        last_scroll = current_time
                    except Exception as e:
                        print(f"Erro no scroll up: {e}")

            # 6.4. Scroll Down
            elif hand_detector.check_scroll_down(fingers) and not drag_active:
                current_time = time.time()
                if current_time - last_scroll > scroll_cooldown:
                    try:
                        pyautogui.scroll(-200)
                        cv2.putText(frame, "SCROLL DOWN", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                        last_scroll = current_time
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Erro no scroll down: {e}")

            # 6.5. Movimento do Mouse
            elif (fingers[1] == 1 and fingers[2] == 1 and
                  all(d == 0 for d in [fingers[3], fingers[4]]) and not drag_active):

                mouse_locked = (fingers[0] == 0)
                if not mouse_locked:
                    cursor_x = (index_x + middle_x) // 2
                    cursor_y = (index_y + middle_y) // 2

                    mapped_x = np.interp(cursor_x, (FRAME_REDUCTION, CAM_WIDTH - FRAME_REDUCTION), (0, screen_width))
                    mapped_y = np.interp(cursor_y, (FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION), (0, screen_height))
                    
                    async_logger.log_calculation('log_coordinate_mapping', cursor_x, cursor_y, mapped_x, mapped_y)

                    curr_cursor_x = prev_cursor_x + (mapped_x - prev_cursor_x) / SMOOTHENING
                    curr_cursor_y = prev_cursor_y + (mapped_y - prev_cursor_y) / SMOOTHENING

                    async_logger.log_calculation('log_mouse_movement', fingers, (cursor_x, cursor_y), (mapped_x, mapped_y),
                                           (curr_cursor_x, curr_cursor_y), mouse_locked)

                    autopy.mouse.move(screen_width - curr_cursor_x, curr_cursor_y)
                    prev_cursor_x, prev_cursor_y = curr_cursor_x, curr_cursor_y

                    cv2.circle(frame, (cursor_x, cursor_y), 12, (255, 0, 255), cv2.FILLED)
                    cv2.line(frame, (index_x, index_y), (middle_x, middle_y), (255, 0, 0), 2)

                status_mouse = "MOUSE TRAVADO" if mouse_locked else "MOUSE LIVRE"
                cv2.putText(frame, status_mouse, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0) if not mouse_locked else (0, 0, 255), 2)

            # 6.6. Clique Direito
            elif (fingers[0] == 0 and fingers[1] == 1 and
                  all(d == 0 for d in [fingers[2], fingers[3], fingers[4]]) and not drag_active):

                current_time = time.time()
                if current_time - last_click > clique_cooldown:
                    try:
                        autopy.mouse.click(autopy.mouse.Button.RIGHT)
                        time.sleep(1.0)  # Adiciona delay de 1s
                        cv2.putText(frame, "CLIQUE DIREITO!", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                        last_click = current_time
                        print("Clique direito executado!")
                        time.sleep(0.2)
                    except Exception as e:
                        print(f"Erro no clique direito: {e}")

            # 6.7. Clique Esquerdo
            elif (fingers[0] == 0 and fingers[2] == 1 and
                  all(d == 0 for d in [fingers[1], fingers[3], fingers[4]]) and not drag_active):

                current_time = time.time()
                if current_time - last_click > clique_cooldown:
                    try:
                        autopy.mouse.click(autopy.mouse.Button.LEFT)
                        time.sleep(1.0)  # Adiciona delay de 1s
                        cv2.putText(frame, "CLIQUE ESQUERDO!", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        last_click = current_time
                        print("Clique esquerdo executado!")
                        time.sleep(0.2)
                    except Exception as e:
                        print(f"Erro no clique esquerdo: {e}")

            # 7. Limpeza do arrasto
            elif drag_active:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                drag_active = False
                print("Arrasto desativado (gesto mudou)")

            # 8. Informações na tela
            stats_fingers = f"P:{fingers[0]} I:{fingers[1]} M:{fingers[2]} A:{fingers[3]} Mi:{fingers[4]}"
            cv2.putText(frame, stats_fingers, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            status_arrasto = "ARRASTO: ATIVO" if drag_active else "ARRASTO: INATIVO"
            cv2.putText(frame, status_arrasto, (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 0, 255) if drag_active else (0, 255, 0), 2)

        # 9. FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time)
        prev_time = curr_time
        cv2.putText(frame, f"FPS: {int(fps)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # 10. Instruções de saída
        cv2.putText(frame, "ESC ou Mao Fechada (3s) para SAIR",
                    (10, CAM_HEIGHT - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # ESC
        if cv2.waitKey(1) & 0xFF == 27:
            break

        # Mão fechada
        if landmarks_list and hand_detector.check_exit_gesture(fingers):
            if not exit_gesture_active:
                exit_gesture_start_time = time.time()
                exit_gesture_active = True

            elapsed_time = time.time() - exit_gesture_start_time
            remaining_time = EXIT_GESTURE_TIME - elapsed_time

            # Feedback visual do gesto de saída
            cv2.putText(frame, f"SAIR: {remaining_time:.1f}s", (10, 270),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Barra de progresso
            progresso = int((elapsed_time / EXIT_GESTURE_TIME) * 100)
            cv2.rectangle(frame, (10, 290), (10 + progresso * 2, 310),
                          (0, 0, 255), cv2.FILLED)
            cv2.rectangle(frame, (10, 290), (210, 310), (255, 255, 255), 2)

            if elapsed_time >= EXIT_GESTURE_TIME:
                cv2.putText(frame, "SAINDO...", (CAM_WIDTH // 2 - 100, CAM_HEIGHT // 2),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                cv2.imshow('Controle de Mouse por Gestos', frame)
                cv2.waitKey(1000)
                break
        else:
            exit_gesture_active = False

        # Display
        cv2.imshow('Controle de Mouse por Gestos', frame)

    # 11. Finalização
    async_logger.stop()
    if drag_active:
        autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

