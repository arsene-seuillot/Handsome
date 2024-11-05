import cv2
import numpy as np
import mediapipe as mp
from picamera2 import Picamera2
import sys

# Vérification du paramètre pour le doigt choisi
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

# Fonction pour calculer l'angle entre deux vecteurs dans un espace 3D
def calculate_angle(v1, v2):
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)

    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0  # Retourner un angle de 0 si l'un des vecteurs est nul

    v1_normalized = v1 / norm_v1  # Normaliser le vecteur v1
    v2_normalized = v2 / norm_v2  # Normaliser le vecteur v2

    dot_product = np.dot(v1_normalized, v2_normalized)  # Calcul du produit scalaire
    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))  # Calcul de l'angle en radians
    return np.degrees(angle_rad)

# Fonction pour calculer les angles entre les phalanges
def calculate_finger_angles(landmarks):
    angles = {}
    
    # Configuration des landmarks pour chaque doigt
    finger_landmarks = {
        'pouce': [1, 2, 3, 4],  # Indices des landmarks du pouce
        'index': [5, 6, 7, 8],  # Indices des landmarks de l'index
        'majeur': [9, 10, 11, 12],  # Indices des landmarks du majeur
        'annulaire': [13, 14, 15, 16],  # Indices des landmarks de l'annulaire
        'auriculaire': [17, 18, 19, 20]  # Indices des landmarks de l'auriculaire
    }

    # Pour chaque doigt, calcul des angles demandés
    for finger_name, indices in finger_landmarks.items():
        angles[finger_name] = {}
        
        if finger_name == 'pouce':
            # Premier angle : entre 1-2 et 2-3
            v1 = np.array([landmarks[2].x - landmarks[1].x,
                           landmarks[2].y - landmarks[1].y,
                           landmarks[2].z - landmarks[1].z])
            v2 = np.array([landmarks[3].x - landmarks[2].x,
                           landmarks[3].y - landmarks[2].y,
                           landmarks[3].z - landmarks[2].z])
            angle1 = calculate_angle(v1, v2)
            angles[finger_name]['pouce_angle_1'] = angle1
            
            # Second angle : entre 2-3 et 3-4
            v1 = np.array([landmarks[3].x - landmarks[2].x,
                           landmarks[3].y - landmarks[2].y,
                           landmarks[3].z - landmarks[2].z])
            v2 = np.array([landmarks[4].x - landmarks[3].x,
                           landmarks[4].y - landmarks[3].y,
                           landmarks[4].z - landmarks[3].z])
            angle2 = calculate_angle(v1, v2)
            angles[finger_name]['pouce_angle_2'] = angle2
            
        # Pour les autres doigts (3 angles)
        else:
            v1 = np.array([landmarks[indices[0] - 4].x - landmarks[0].x,
                           landmarks[indices[0] - 4].y - landmarks[0].y,
                           landmarks[indices[0] - 4].z - landmarks[0].z])
            v2 = np.array([landmarks[indices[1]].x - landmarks[indices[0]].x,
                           landmarks[indices[1]].y - landmarks[indices[0]].y,
                           landmarks[indices[1]].z - landmarks[indices[0]].z])
            angle1 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_1'] = angle1

            v1 = np.array([landmarks[indices[1]].x - landmarks[indices[0]].x,
                           landmarks[indices[1]].y - landmarks[indices[0]].y,
                           landmarks[indices[1]].z - landmarks[indices[0]].z])
            v2 = np.array([landmarks[indices[2]].x - landmarks[indices[1]].x,
                           landmarks[indices[2]].y - landmarks[indices[1]].y,
                           landmarks[indices[2]].z - landmarks[indices[1]].z])
            angle2 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_2'] = angle2

            v1 = np.array([landmarks[indices[2]].x - landmarks[indices[1]].x,
                           landmarks[indices[2]].y - landmarks[indices[1]].y,
                           landmarks[indices[2]].z - landmarks[indices[1]].z])
            v2 = np.array([landmarks[indices[3]].x - landmarks[indices[2]].x,
                           landmarks[indices[3]].y - landmarks[indices[2]].y,
                           landmarks[indices[3]].z - landmarks[indices[2]].z])
            angle3 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_3'] = angle3

    return angles

# Boucle principale de traitement sans affichage
try:
    while True:
        # Capture de l'image
        frame = picam2.capture_array()
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Conversion en RGB pour MediaPipe
        results = hands.process(rgb_frame)

        # Traitement des résultats
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Calcul des angles des doigts
                finger_angles = calculate_finger_angles(hand_landmarks.landmark)
                dic_angles = finger_angles.get(param, {})

                # Affichage dans le terminal
                for clé, valeur in dic_angles.items():
                    print(clé, valeur)

except KeyboardInterrupt:
    print("Arrêt du programme")
finally:
    # Arrêter la caméra proprement
    picam2.stop()

