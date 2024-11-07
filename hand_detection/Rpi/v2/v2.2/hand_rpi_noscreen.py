import cv2
import numpy as np
import mediapipe as mp
from collections import deque  # Import de deque pour la moyenne glissante
from picamera2 import Picamera2
import sys

# Vérification de l'argument d'entrée pour sélectionner un doigt
if len(sys.argv) < 2:
    print("Il faut choisir un doigt en paramètre. L'index a été choisi par défaut")
    param = "index"
else:
    param = sys.argv[1]

# Initialisation de MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Initialisation de Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Classe pour gérer la moyenne glissante des coordonnées
class SlidingAverage:
    def __init__(self, window_size=3):
        self.window_size = window_size
        self.landmarks_buffer = {i: {'x': deque(maxlen=window_size),
                                     'y': deque(maxlen=window_size),
                                     'z': deque(maxlen=window_size)}
                                 for i in range(21)}  # 21 landmarks pour une main

    def update(self, landmarks):
        smoothed_landmarks = []

        for i, landmark in enumerate(landmarks):
            # Ajout des nouvelles valeurs au buffer
            self.landmarks_buffer[i]['x'].append(landmark.x)
            self.landmarks_buffer[i]['y'].append(landmark.y)
            self.landmarks_buffer[i]['z'].append(landmark.z)

            # Calcul de la moyenne glissante
            smoothed_x = sum(self.landmarks_buffer[i]['x']) / len(self.landmarks_buffer[i]['x'])
            smoothed_y = sum(self.landmarks_buffer[i]['y']) / len(self.landmarks_buffer[i]['y'])
            smoothed_z = sum(self.landmarks_buffer[i]['z']) / len(self.landmarks_buffer[i]['z'])

            smoothed_landmarks.append({'x': smoothed_x, 'y': smoothed_y, 'z': smoothed_z})

        return smoothed_landmarks

# Instanciation de l'outil de moyenne glissante
sliding_average = SlidingAverage(window_size=3)

# Fonction pour calculer l'angle entre deux vecteurs en 3D
def calculate_angle(v1, v2):
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0

    v1_normalized = v1 / norm_v1
    v2_normalized = v2 / norm_v2

    dot_product = np.dot(v1_normalized, v2_normalized)
    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))
    return np.degrees(angle_rad)

# Fonction pour calculer les angles des phalanges de chaque doigt
def calculate_finger_angles(landmarks):
    angles = {}
    finger_landmarks = {
        'pouce': [1, 2, 3, 4],
        'index': [5, 6, 7, 8],
        'majeur': [9, 10, 11, 12],
        'annulaire': [13, 14, 15, 16],
        'auriculaire': [17, 18, 19, 20]
    }

    for finger_name, indices in finger_landmarks.items():
        angles[finger_name] = {}

        if finger_name == 'pouce':
            v1 = np.array([landmarks[2]['x'] - landmarks[1]['x'],
                           landmarks[2]['y'] - landmarks[1]['y'],
                           landmarks[2]['z'] - landmarks[1]['z']])
            v2 = np.array([landmarks[3]['x'] - landmarks[2]['x'],
                           landmarks[3]['y'] - landmarks[2]['y'],
                           landmarks[3]['z'] - landmarks[2]['z']])
            angle1 = calculate_angle(v1, v2)
            angles[finger_name]['pouce_angle_1'] = angle1

            v1 = np.array([landmarks[3]['x'] - landmarks[2]['x'],
                           landmarks[3]['y'] - landmarks[2]['y'],
                           landmarks[3]['z'] - landmarks[2]['z']])
            v2 = np.array([landmarks[4]['x'] - landmarks[3]['x'],
                           landmarks[4]['y'] - landmarks[3]['y'],
                           landmarks[4]['z'] - landmarks[3]['z']])
            angle2 = calculate_angle(v1, v2)
            angles[finger_name]['pouce_angle_2'] = angle2

        else:
            v1 = np.array([landmarks[indices[0] - 4]['x'] - landmarks[0]['x'],
                           landmarks[indices[0] - 4]['y'] - landmarks[0]['y'],
                           landmarks[indices[0] - 4]['z'] - landmarks[0]['z']])
            v2 = np.array([landmarks[indices[1]]['x'] - landmarks[indices[0]]['x'],
                           landmarks[indices[1]]['y'] - landmarks[indices[0]]['y'],
                           landmarks[indices[1]]['z'] - landmarks[indices[0]]['z']])
            angle1 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_1'] = angle1

            v1 = np.array([landmarks[indices[1]]['x'] - landmarks[indices[0]]['x'],
                           landmarks[indices[1]]['y'] - landmarks[indices[0]]['y'],
                           landmarks[indices[1]]['z'] - landmarks[indices[0]]['z']])
            v2 = np.array([landmarks[indices[2]]['x'] - landmarks[indices[1]]['x'],
                           landmarks[indices[2]]['y'] - landmarks[indices[1]]['y'],
                           landmarks[indices[2]]['z'] - landmarks[indices[1]]['z']])
            angle2 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_2'] = angle2

            v1 = np.array([landmarks[indices[2]]['x'] - landmarks[indices[1]]['x'],
                           landmarks[indices[2]]['y'] - landmarks[indices[1]]['y'],
                           landmarks[indices[2]]['z'] - landmarks[indices[1]]['z']])
            v2 = np.array([landmarks[indices[3]]['x'] - landmarks[indices[2]]['x'],
                           landmarks[indices[3]]['y'] - landmarks[indices[2]]['y'],
                           landmarks[indices[3]]['z'] - landmarks[indices[2]]['z']])
            angle3 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_3'] = angle3

    return angles

# Boucle principale pour le traitement de chaque frame
while True:
    frame = picam2.capture_array()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            smoothed_landmarks = sliding_average.update(hand_landmarks.landmark)
            finger_angles = calculate_finger_angles(smoothed_landmarks)
            print(finger_angles)
            dic_angles = finger_angles[param] # pour l'exemple, dico des angles d'un seul doigt         
            ###### ENVOYER LES DONNÉES ######
		
            #for key, value in dic_angles.items():
                #print(f"{key}: {value}")

# Arrêter la caméra lorsque le programme est terminé
picam2.stop()

