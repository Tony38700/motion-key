import threading
import time
from collections import deque

class AsyncLogger:
    def __init__(self, gesture_logger, calculation_logger, batch_interval=5.0):
        self.gesture_logger = gesture_logger
        self.calculation_logger = calculation_logger
        self.batch_interval = batch_interval

        self.gesture_queue = deque()
        self.calculation_queue = deque()
        self.last_batch_time = time.time()

        self.running = True
        self.thread = threading.Thread(target=self._process_queues, daemon=True)
        self.thread.start()

    def log_gesture(self, fingers, landmarks_list=None, hand_detector=None, confidence=None, bounding_box=None):
        self.gesture_queue.append({
            'fingers': fingers,
            'landmarks_list': landmarks_list,
            'hand_detector': hand_detector,
            'confidence': confidence,
            'bounding_box': bounding_box
        })

    def log_calculation(self, method_name, *args):
        self.calculation_queue.append({
            'method': method_name,
            'args': args
        })

    def _process_queues(self):
        while self.running:
            current_time = time.time()

            # Processa em lotes a cada intervalo
            if current_time - self.last_batch_time >= self.batch_interval:
                self._process_batch()
                self.last_batch_time = current_time

            time.sleep(0.1)  # Pequena pausa para não sobrecarregar

    def _process_batch(self):
        # Processa apenas o último gesto (evita repetição)
        if self.gesture_queue:
            last_gesture = self.gesture_queue[-1]
            self.gesture_logger.log_gesture(**last_gesture)
            self.gesture_queue.clear()

        # Processa apenas os últimos 5 calculation logs (limita quantidade)
        if self.calculation_queue:
            recent_calculations = list(self.calculation_queue)[-5:]  # Últimos 5
            for calculation in recent_calculations:
                method = getattr(self.calculation_logger, calculation['method'])
                method(*calculation['args'])
            self.calculation_queue.clear()

    def stop(self):
        self.running = False

        self.thread.join()
