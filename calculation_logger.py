import requests

class DebugLogger:
    def __init__(self, api_base_url="http://localhost:5000/api"):
        self.api_base_url = api_base_url

    def send_to_api(self, debug_data):
        try:
            response = requests.post(f"{self.api_base_url}/calculations", json=debug_data, timeout=5)
            return response.status_code == 201
        except requests.exceptions.ConnectionError:
            print("Erro: Não foi possível conectar à API")
            return False
        except requests.exceptions.Timeout:
            print("Erro: Timeout na conexão com a API")
            return False
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição: {e}")
            return False

    def log_mouse_movement(self, fingers, cursor_pos, screen_pos, smoothed_pos, mouse_locked):
        debug_data = {
            "operation_type": "MOUSE_MOVEMENT",
            "input_data": {
                "fingers": fingers,
                "raw_cursor_pos": cursor_pos,
                "mouse_locked": mouse_locked
            },
            "output_data": {
                "screen_position": screen_pos,
                "smoothed_position": smoothed_pos
            },
            "result": f"Mouse {'TRAVADO' if mouse_locked else 'MOVENDO'}",
            "additional_info": {"smoothening_factor": 7}
        }
        return self.send_to_api(debug_data)

    def log_drag_operation(self, fingers, thumb_pos, index_pos, distance, drag_active):
        debug_data = {
            "operation_type": "DRAG_OPERATION",
            "input_data": {
                "fingers": fingers,
                "thumb_position": thumb_pos,
                "index_position": index_pos,
                "distance": distance
            },
            "output_data": {
                "drag_active": drag_active
            },
            "result": f"Drag {'ATIVADO' if drag_active else 'DESATIVADO'}",
            "additional_info": {"threshold": 20, "current_distance": distance}
        }
        return self.send_to_api(debug_data)

    def log_coordinate_mapping(self, raw_x, raw_y, mapped_x, mapped_y):
        debug_data = {
            "operation_type": "COORDINATE_MAPPING",
            "input_data": {
                "raw_camera_x": raw_x,
                "raw_camera_y": raw_y
            },
            "output_data": {
                "mapped_screen_x": mapped_x,
                "mapped_screen_y": mapped_y
            },
            "result": f"Mapped: ({mapped_x:.1f}, {mapped_y:.1f})",
            "additional_info": {"frame_reduction": 100}
        }
        return self.send_to_api(debug_data)

    def log_distance_calculation(self, point1, point2, distance):
        debug_data = {
            "operation_type": "DISTANCE_CALCULATION",
            "input_data": {
                "point1": f"ID:{point1[0]} ({point1[1]},{point1[2]})",
                "point2": f"ID:{point2[0]} ({point2[1]},{point2[2]})"
            },
            "output_data": {
                "calculated_distance": distance
            },
            "result": f"Distance: {distance:.2f}",
            "additional_info": {"threshold": 20, "within_threshold": distance < 20}
        }
        return self.send_to_api(debug_data)

    def log_finger_positions(self, landmarks_list):
        finger_positions = {}
        finger_names = ["POLEGAR", "INDICADOR", "MEDIO", "ANELAR", "MINDINHO"]

        for i, finger_id in enumerate([4, 8, 12, 16, 20]):
            if len(landmarks_list) > finger_id:
                x, y = landmarks_list[finger_id][1], landmarks_list[finger_id][2]
                finger_positions[finger_names[i]] = (x, y)

        debug_data = {
            "operation_type": "FINGER_POSITIONS",
            "input_data": {"landmarks_count": len(landmarks_list)},
            "output_data": {"finger_positions": finger_positions},
            "result": "Posições dos dedos capturadas",
            "additional_info": {"total_fingers_tracked": len(finger_positions)}
        }
        return self.send_to_api(debug_data)

    def log_hand_geometry(self, landmarks_list):
        if len(landmarks_list) < 21:
            return False

        distances = {}
        finger_pairs = [
            ("POLEGAR-INDICADOR", 4, 8),
            ("POLEGAR-MEDIO", 4, 12),
            ("POLEGAR-ANELAR", 4, 16),
            ("POLEGAR-MINDINHO", 4, 20),
            ("INDICADOR-MEDIO", 8, 12),
            ("MEDIO-ANELAR", 12, 16),
            ("ANELAR-MINDINHO", 16, 20)
        ]

        for name, id1, id2 in finger_pairs:
            dist = ((landmarks_list[id1][1] - landmarks_list[id2][1]) ** 2 +
                    (landmarks_list[id1][2] - landmarks_list[id2][2]) ** 2) ** 0.5
            distances[name] = dist

        debug_data = {
            "operation_type": "HAND_GEOMETRY",
            "input_data": {"landmarks_available": True},
            "output_data": {"finger_distances": distances},
            "result": "Geometria da mão calculada",
            "additional_info": {"total_distances_calculated": len(distances)}
        }
        return self.send_to_api(debug_data)

    def log_double_click(self, fingers):
        debug_data = {
            "operation_type": "DOUBLE_CLICK",
            "input_data": {"fingers": fingers},
            "output_data": {"executed": True},
            "result": "Clique duplo executado",
            "additional_info": {"cooldown": 2.0}
        }
        return self.send_to_api(debug_data)