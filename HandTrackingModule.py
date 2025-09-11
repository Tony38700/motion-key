import cv2
import mediapipe as mp
import time
import math
import numpy as np


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode #imagem modo estatica ou video
        self.maxHands = maxHands #maximo de mãos detectadas
        self.detectionCon = detectionCon #confiança minima para detecção
        self.trackCon = trackCon ##confiança minima para rastreamento

        #mediapipe hands
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils #ferraemntas para desenhos
        self.tipIds = [4, 8, 12, 16, 20] #ID dos dedos: polegar, indicador, médio, anelar e mindinho

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #BGR para RPG
        self.results = self.hands.process(imgRGB) #detectar mãos
        # print(results.multi_hand_landmarks)

        #variável para armazenar confiança
        self.detection_confidence = 0.0

        #desenha landmarks nas mãos
        if self.results.multi_hand_landmarks:
            if self.results.multi_handedness:
                handedness = self.results.multi_handedness[0]
                self.detection_confidence = handedness.classification[0].score * 100  # Converte para porcentagem

            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        xList = []
        yList = []
        bbox = []
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo] #preferencia para primeira mão

            #coordenadas para pixel
            for id, lm in enumerate(myHand.landmark):
                # print(id, lm)
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                # print(id, cx, cy)
                self.lmList.append([id, cx, cy]) #armazena ID, coordenadas xy
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20),
                              (0, 255, 0), 2)

        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        if not hasattr(self, 'lmList') or len(self.lmList) == 0:
            return [0, 0, 0, 0, 0]  # retorna todos os dedos abaixados se não detectar mão

        # Thumb
        if self.lmList[self.tipIds[0]][1] < self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)  #polegar aberto
        else:
            fingers.append(0)  #polegar fechado

        # dedos
        for id in range(1, 5):

            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1) #dedo levantado
            else:
                fingers.append(0) #dedo abaixado

        return fingers #lista de dedos levantados ou não

    def findDistance(self, p1, p2, img, draw=True,r=15, t=3):
        x1, y1 = self.lmList[p1][1:] #coordenadas do ponto 1
        x2, y2 = self.lmList[p2][1:] #coordenadas do ponto 2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2 #centro entre os pontos

        #circulos
        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t) #entre pontos
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED) #no ponto 1
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED) #no ponto 2
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED) #central
        length = math.hypot(x2 - x1, y2 - y1) #distancia media entre os pontos

        return length, img, [x1, y1, x2, y2, cx, cy]