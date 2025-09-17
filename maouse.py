import cv2
import numpy as np
import HandTrackingModule as htm
import time
import autopy

###configurações/variaveis####
wCam, hCam = 640, 480 #resolução da camera
frameR = 100 # redução de frame
smoothening = 7 #suavização do movimento dos dedos
#webcam
cap = cv2.VideoCapture(0) #0 - câmera padrão; 1 - câmera externa
cap.set(3, wCam) #largura
cap.set(4, hCam) #altura
#tempo e detecção
pTime = 0 #variavel tempo do FPS
detector = htm.handDetector(maxHands=1) #uma mão por vez
#tela
wScr, hScr = autopy.screen.size() #capturar a resolução da tela
    #print("Resolução da tela:", wScr, hScr)
plocX, plocY = 0, 0 #posição anterior do cursor (suavização)
clocX, clocY = 0, 0 #posição atual do cursor (suavização)
##############################

# Verifica se a câmera abriu corretamente
if not cap.isOpened():
    print("Não foi possível abrir a câmera.")
    exit()

while True:
    #1.Encontrar pontos de referência para as mãos
    success, img = cap.read() #captura frame da webcam
    img = detector.findHands(img) #chama classe handdetector
    lmList, bbox = detector.findPosition(img) #parametro da img

    #2.Pegar a ponta dos dedos indicador(1) e médio(2)
    x1 = y1 = x2 = y2 = 0 #variáveis
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:] #ponto 8
        x2, y2 = lmList[12][1:] #ponto 12
        #print(x1, y1, x2, y2)

    #3.Verificar quais dedos estão levantados
    fingers = detector.fingersUp()
    #print(fingers)
    cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                  (255, 0, 255), 2) #limitação do mouse na webcam

    #metodo de confiaça
    if hasattr(detector, 'detection_confidence') and detector.detection_confidence > 0: #garante confiança maior que 0
        conf_text = f"Confianca: {detector.detection_confidence:.1f}%" #mostra na tela e arredonda para uma casa decimal
        cv2.putText(img, conf_text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, #define posição xy, fonte, tamano da fonte, cor(verde), espessura
                    0.7, (0, 255, 0), 2)

    #4.Apenas dedo indicador: modo de movimento
    if fingers[1] == 1 and fingers[2] == 0:
        #4.1.Converter coordenadas da webcam para o monitor
        x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
        y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
        #4.2.Suavizar valores
        clocX = plocX + (x3 - plocX) / smoothening #em x
        clocY = plocY + (y3 - plocY) / smoothening #em y
        #4.3.Mover o mouse
        autopy.mouse.move(wScr - clocX, clocY) #inverte eixo X para movimento espelhado
        cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED) #marcar mouse em roxo
        plocX, plocY = clocX, clocY #próximo frame

    #5.Se dedo indicador e médio estiverem levantados: Modo de clique
    if fingers[1] == 1 and fingers[2] == 1:
        #5.1.Encontrar a distância entre os dedos
        length, img, lineInfo = detector.findDistance(8, 12, img)
        print(length)
        #5.2.Clicar com o mouse se a distância for curta
        if length < 40:
            cv2.circle(img, (lineInfo[4], lineInfo[5]),
                       15, (0, 255, 0), cv2.FILLED) #confirmar click com circulo verde
            autopy.mouse.click()
    #6.FPS
    cTime = time.time() #tempo atual
    fps = 1 / (cTime - pTime) #calcula FPS
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3) #fps em azul

    #7.Display
    cv2.imshow('Image', img) #cria janela
    # Pressione 'esc' para sair do loop
    if cv2.waitKey(1) & 0xFF == 27: # 27 é o código ASCII da tecla ESC
        break

# Libera recursos após sair do loop
cap.release()

cv2.destroyAllWindows()

