import requests
import time


class GestureLogger:
    def __init__(self, api_base_url="http://localhost:5000/api", log_interval=1.0):
        self.api_base_url = api_base_url
        self.log_interval = log_interval
        self.last_log_time = 0
        self.last_gesture = None

    @staticmethod
    def get_gesture_name(fingers, landmarks_list=None, hand_detector=None):
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1:
            return "MOVIMENTO_MOUSE"

        elif fingers[0] == 0 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            if landmarks_list and hand_detector:
                distancia = hand_detector.get_distance(landmarks_list[4], landmarks_list[8])
                if distancia < 20:
                    return "ARRASTO"

        elif fingers[2] == 1 and all(d == 0 for d in [fingers[0], fingers[1], fingers[3], fingers[4]]):
            return "CLIQUE_ESQUERDO"

        elif fingers[1] == 1 and all(d == 0 for d in [fingers[0], fingers[2], fingers[3], fingers[4]]):
            return "CLIQUE_DIREITO"

        elif all(d == 0 for d in fingers):
            return "CLIQUE_DUPLO"

        elif fingers[0] == 1 and fingers[1] == 1 and all(d == 0 for d in fingers[2:]):
            return "SCROLL_UP"

        elif fingers[0] == 1 and fingers[4] == 1 and all(d == 0 for d in fingers[1:4]):
            return "SCROLL_DOWN"

        elif fingers[0] == 1 and all(d == 0 for d in fingers[1:]):
            return "GESTO_SAIDA"

        return "GESTO_DESCONHECIDO"

    def should_log(self, current_time, current_gesture):
        time_ok = current_time - self.last_log_time >= self.log_interval
        gesture_changed = current_gesture != self.last_gesture
        return time_ok or gesture_changed

    def send_to_api(self, gesture_data):
        try:
            response = requests.post(f"{self.api_base_url}/gestures", json=gesture_data, timeout=5)
            return response.status_code == 201
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return False

    def log_gesture(self, fingers, landmarks_list=None, hand_detector=None, confidence=None, bounding_box=None):
        current_time = time.time()
        current_gesture = self.get_gesture_name(fingers, landmarks_list, hand_detector)

        if current_gesture == "GESTO_DESCONHECIDO":
            return False

        if not self.should_log(current_time, current_gesture):
            return False

        gesture_data = {
            "fingers": fingers,
            "gesture_name": current_gesture,
            "confidence": confidence,
            "hand_position": bounding_box,
            "landmarks": landmarks_list
        }

        success = self.send_to_api(gesture_data)

        if success:
            self.last_log_time = current_time
            self.last_gesture = current_gesture

        return success