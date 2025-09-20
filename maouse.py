import cv2
import numpy as np
import time
import autopy
import pyautogui # Para scroll
from hand_tracking_module import HandDetector, verificar_dedos_levantados, \
    verificar_gesto_saida, verificar_clique_duplo, verificar_scroll_up, \
    verificar_scroll_down

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
    # 1. inicialização
    camera = cv2.VideoCapture(0)
    camera.set(3, CAM_WIDTH)
    camera.set(4, CAM_HEIGHT)

    # Configurações de detecção
    prev_time = 0
    hand_detector = HandDetector(max_hands=1)

    # Configurações de tela e movimento
    screen_width, screen_height = autopy.screen.size()
    prev_cursor_x, prev_cursor_y = 0, 0  # Mouse normal
    curr_cursor_x, curr_cursor_y = 0, 0
    prev_drag_x, prev_drag_y = 0, 0  # Arrasto
    curr_drag_x, curr_drag_y = 0, 0

    # 2. Estados das variáveis
    mouse_travado = False
    drag_ativo = False
    ultimo_clique = 0
    ultimo_duplo_clique = 0
    ultimo_scroll = 0
    clique_cooldown = 1.0
    scroll_cooldown = 0.5
    exit_gesture_start_time = 0
    exit_gesture_active = False

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
            dedos = verificar_dedos_levantados(landmarks_list)
            thumb_x, thumb_y = landmarks_list[4][1], landmarks_list[4][2]
            index_x, index_y = landmarks_list[8][1], landmarks_list[8][2]
            middle_x, middle_y = landmarks_list[12][1], landmarks_list[12][2]
            ring_x, ring_y = landmarks_list[16][1], landmarks_list[16][2]
            pinky_x, pinky_y = landmarks_list[20][1], landmarks_list[20][2]

            # 5. Metodo de confiança
            if hasattr(hand_detector, 'detection_confidence') and hand_detector.detection_confidence > 0:
                conf_text = f"Confianca: {hand_detector.detection_confidence:.1f}%"
                cv2.putText(frame, conf_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX,
                            0.7, (0, 255, 0), 2)

            # 6. GESTOS PRINCIPAIS
            # 6.1. Clique Duplo
            if verificar_clique_duplo(dedos) and not drag_ativo:
                tempo_atual = time.time()
                if tempo_atual - ultimo_duplo_clique > DOUBLE_CLICK_COOLDOWN:
                    try:
                        autopy.mouse.click(autopy.mouse.Button.LEFT)
                        time.sleep(0.1)
                        autopy.mouse.click(autopy.mouse.Button.LEFT)
                        cv2.putText(frame, "CLIQUE DUPLO!", (10, 240),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                        ultimo_duplo_clique = tempo_atual
                        print("Clique duplo executado!")
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"Erro no clique duplo: {e}")

            # 6.2. Arrasto
            elif (dedos[0] == 0 and dedos[2] == 1 and
                  dedos[3] == 1 and dedos[4] == 1):
                distancia = hand_detector.get_distance(landmarks_list[4], landmarks_list[8])

                if distancia < DRAG_DISTANCE_THRESHOLD:
                    cv2.circle(frame, (thumb_x, thumb_y), 10, (0, 255, 255), cv2.FILLED)
                    cv2.circle(frame, (index_x, index_y), 10, (0, 255, 255), cv2.FILLED)
                    cv2.line(frame, (thumb_x, thumb_y), (index_x, index_y), (0, 255, 255), 2)
                    cv2.putText(frame, f"Dist: {int(distancia)}", (thumb_x, thumb_y - 15),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

                if distancia < DRAG_DISTANCE_THRESHOLD:
                    if not drag_ativo:
                        autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                        drag_ativo = True
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
                else:
                    if drag_ativo:
                        autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                        drag_ativo = False
                        cv2.putText(frame, "ARRASTO LIBERADO", (10, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        print("Arrasto desativado")

            # 6.3. Scroll Up
            elif verificar_scroll_up(dedos) and not drag_ativo:
                tempo_atual = time.time()
                if tempo_atual - ultimo_scroll > scroll_cooldown:
                    try:
                        pyautogui.scroll(200)
                        cv2.putText(frame, "SCROLL UP", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                        ultimo_scroll = tempo_atual
                    except Exception as e:
                        print(f"Erro no scroll up: {e}")

            # 6.4. Scroll Down
            elif verificar_scroll_down(dedos) and not drag_ativo:
                tempo_atual = time.time()
                if tempo_atual - ultimo_scroll > scroll_cooldown:
                    try:
                        pyautogui.scroll(-200)
                        cv2.putText(frame, "SCROLL DOWN", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 165, 0), 2)
                        ultimo_scroll = tempo_atual
                        time.sleep(0.1)
                    except Exception as e:
                        print(f"Erro no scroll down: {e}")

            # 6.5. Movimento do Mouse
            elif (dedos[1] == 1 and dedos[2] == 1 and
                  all(d == 0 for d in [dedos[3], dedos[4]]) and not drag_ativo):

                mouse_travado = (dedos[0] == 0)
                if not mouse_travado:
                    cursor_x = (index_x + middle_x) // 2
                    cursor_y = (index_y + middle_y) // 2

                    mapped_x = np.interp(cursor_x, (FRAME_REDUCTION, CAM_WIDTH - FRAME_REDUCTION), (0, screen_width))
                    mapped_y = np.interp(cursor_y, (FRAME_REDUCTION, CAM_HEIGHT - FRAME_REDUCTION), (0, screen_height))

                    curr_cursor_x = prev_cursor_x + (mapped_x - prev_cursor_x) / SMOOTHENING
                    curr_cursor_y = prev_cursor_y + (mapped_y - prev_cursor_y) / SMOOTHENING

                    autopy.mouse.move(screen_width - curr_cursor_x, curr_cursor_y)
                    prev_cursor_x, prev_cursor_y = curr_cursor_x, curr_cursor_y

                    cv2.circle(frame, (cursor_x, cursor_y), 12, (255, 0, 255), cv2.FILLED)
                    cv2.line(frame, (index_x, index_y), (middle_x, middle_y), (255, 0, 0), 2)

                status_mouse = "MOUSE TRAVADO" if mouse_travado else "MOUSE LIVRE"
                cv2.putText(frame, status_mouse, (10, 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (0, 255, 0) if not mouse_travado else (0, 0, 255), 2)

            # 6.6. Clique Direito
            elif (dedos[0] == 0 and dedos[1] == 1 and
                  all(d == 0 for d in dedos[2:]) and not drag_ativo):

                tempo_atual = time.time()
                if tempo_atual - ultimo_clique > clique_cooldown:
                    try:
                        autopy.mouse.click(autopy.mouse.Button.RIGHT)
                        time.sleep(1.0)  # Adiciona delay de 1s
                        cv2.putText(frame, "CLIQUE DIREITO!", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                        ultimo_clique = tempo_atual
                        print("Clique direito executado!")
                        time.sleep(0.2)
                    except Exception as e:
                        print(f"Erro no clique direito: {e}")

            # 6.7. Clique Esquerdo
            elif (dedos[0] == 0 and dedos[2] == 1 and
                  dedos[1] == 0 and all(d == 0 for d in [dedos[3], dedos[4]]) and not drag_ativo):

                tempo_atual = time.time()
                if tempo_atual - ultimo_clique > clique_cooldown:
                    try:
                        autopy.mouse.click(autopy.mouse.Button.LEFT)
                        time.sleep(1.0)  # Adiciona delay de 1s
                        cv2.putText(frame, "CLIQUE ESQUERDO!", (10, 210),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        ultimo_clique = tempo_atual
                        print("Clique esquerdo executado!")
                        time.sleep(0.2)
                    except Exception as e:
                        print(f"Erro no clique esquerdo: {e}")

            # 7. Limpeza do arrasto
            elif drag_ativo:
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
                drag_ativo = False
                print("Arrasto desativado (gesto mudou)")

            # 8. Informações na tela
            status_dedos = f"P:{dedos[0]} I:{dedos[1]} M:{dedos[2]} A:{dedos[3]} Mi:{dedos[4]}"
            cv2.putText(frame, status_dedos, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            status_arrasto = "ARRASTO: ATIVO" if drag_ativo else "ARRASTO: INATIVO"
            cv2.putText(frame, status_arrasto, (10, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                        (0, 0, 255) if drag_ativo else (0, 255, 0), 2)

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
        if landmarks_list and verificar_gesto_saida(dedos):
            if not exit_gesture_active:
                exit_gesture_start_time = time.time()
                exit_gesture_active = True

            tempo_decorrido = time.time() - exit_gesture_start_time
            tempo_restante = EXIT_GESTURE_TIME - tempo_decorrido

            # Feedback visual do gesto de saída
            cv2.putText(frame, f"SAIR: {tempo_restante:.1f}s", (10, 270),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # Barra de progresso
            progresso = int((tempo_decorrido / EXIT_GESTURE_TIME) * 100)
            cv2.rectangle(frame, (10, 290), (10 + progresso * 2, 310),
                          (0, 0, 255), cv2.FILLED)
            cv2.rectangle(frame, (10, 290), (210, 310), (255, 255, 255), 2)

            if tempo_decorrido >= EXIT_GESTURE_TIME:
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
    if drag_ativo:
        autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
