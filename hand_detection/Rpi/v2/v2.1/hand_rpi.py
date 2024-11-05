import cv2
import numpy as np
import mediapipe as mp
from math import sqrt
from picamera2 import Picamera2
import tkinter as tk
from PIL import Image, ImageTk
import sys
from collections import deque

if len(sys.argv) < 2:
    print("Il faut choisir un doigt en paramètre. L'index a été choisi par défaut")
    param = "index"
else:
    param = sys.argv[1]

# Initialisation de MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Initialisation de Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)})
picam2.configure(config)
picam2.start()

# Création de la fenêtre Tkinter
root = tk.Tk()
root.title("Détection des Mains avec MediaPipe")

# Création d'un label pour afficher les images
image_label = tk.Label(root)
image_label.pack()

# Définir une classe pour gérer la moyenne glissante sur les coordonnées
class SlidingAverage:
    def __init__(self, window_size=5):
        self.window_size = window_size
        self.landmarks_buffer = {i: {'x': deque(maxlen=window_size),
                                     'y': deque(maxlen=window_size),
                                     'z': deque(maxlen=window_size)}
                                 for i in range(21)}  # 21 landmarks pour une main

    # Ajoute les nouvelles coordonnées et renvoie les coordonnées lissées
    def update(self, landmarks):
        smoothed_landmarks = []

        for i, landmark in enumerate(landmarks):
            # Ajouter les nouvelles valeurs au buffer
            self.landmarks_buffer[i]['x'].append(landmark.x)
            self.landmarks_buffer[i]['y'].append(landmark.y)
            self.landmarks_buffer[i]['z'].append(landmark.z)

            # Calculer la moyenne glissante pour chaque coordonnée
            smoothed_x = sum(self.landmarks_buffer[i]['x']) / len(self.landmarks_buffer[i]['x'])
            smoothed_y = sum(self.landmarks_buffer[i]['y']) / len(self.landmarks_buffer[i]['y'])
            smoothed_z = sum(self.landmarks_buffer[i]['z']) / len(self.landmarks_buffer[i]['z'])

            # Stocker les coordonnées lissées
            smoothed_landmarks.append({
                'x': smoothed_x,
                'y': smoothed_y,
                'z': smoothed_z
            })

        return smoothed_landmarks

# On prend une fenêtre de taille 3 : meilleur compromis entre rapidité et précision.
sliding_average = SlidingAverage(window_size=3)

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
        'pouce': [1, 2, 3, 4],
        'index': [5, 6, 7, 8],
        'majeur': [9, 10, 11, 12],
        'annulaire': [13, 14, 15, 16],
        'auriculaire': [17, 18, 19, 20]
    }

    # Pour chaque doigt, calcul des angles demandés
    for finger_name, indices in finger_landmarks.items():
        angles[finger_name] = {}
        
        if finger_name == 'pouce':
            v1 = np.array([
                landmarks[2]['x'] - landmarks[1]['x'],
                landmarks[2]['y'] - landmarks[1]['y'],
                landmarks[2]['z'] - landmarks[1]['z']
            ])
            v2 = np.array([
                landmarks[3]['x'] - landmarks[2]['x'],
                landmarks[3]['y'] - landmarks[2]['y'],
                landmarks[3]['z'] - landmarks[2]['z']
            ])
            angle1 = calculate_angle(v1, v2)
            angles[finger_name]['pouce_angle_1'] = angle1
            
            v1 = np.array([
                landmarks[3]['x'] - landmarks[2]['x'],
                landmarks[3]['y'] - landmarks[2]['y'],
                landmarks[3]['z'] - landmarks[2]['z']
            ])
            v2 = np.array([
                landmarks[4]['x'] - landmarks[3]['x'],
                landmarks[4]['y'] - landmarks[3]['y'],
                landmarks[4]['z'] - landmarks[3]['z']
            ])
            angle2 = calculate_angle(v1, v2)
            angles[finger_name]['pouce_angle_2'] = angle2
            
        else:
            v1 = np.array([
                landmarks[indices[0] - 4]['x'] - landmarks[0]['x'],
                landmarks[indices[0] - 4]['y'] - landmarks[0]['y'],
                landmarks[indices[0] - 4]['z'] - landmarks[0]['z']
            ])
            v2 = np.array([
                landmarks[indices[1]]['x'] - landmarks[indices[0]]['x'],
                landmarks[indices[1]]['y'] - landmarks[indices[0]]['y'],
                landmarks[indices[1]]['z'] - landmarks[indices[0]]['z']
            ])
            angle1 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_1'] = angle1

            v1 = np.array([
                landmarks[indices[1]]['x'] - landmarks[indices[0]]['x'],
                landmarks[indices[1]]['y'] - landmarks[indices[0]]['y'],
                landmarks[indices[1]]['z'] - landmarks[indices[0]]['z']
            ])
            v2 = np.array([
                landmarks[indices[2]]['x'] - landmarks[indices[1]]['x'],
                landmarks[indices[2]]['y'] - landmarks[indices[1]]['y'],
                landmarks[indices[2]]['z'] - landmarks[indices[1]]['z']
            ])
            angle2 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_2'] = angle2

            v1 = np.array([
                landmarks[indices[2]]['x'] - landmarks[indices[1]]['x'],
                landmarks[indices[2]]['y'] - landmarks[indices[1]]['y'],
                landmarks[indices[2]]['z'] - landmarks[indices[1]]['z']
            ])
            v2 = np.array([
                landmarks[indices[3]]['x'] - landmarks[indices[2]]['x'],
                landmarks[indices[3]]['y'] - landmarks[indices[2]]['y'],
                landmarks[indices[3]]['z'] - landmarks[indices[2]]['z']
            ])
            angle3 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_3'] = angle3

    return angles



def update_frame():
    frame = picam2.capture_array()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(rgb_frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Calcul des angles des doigts avec coordonnées lissées
            smoothed_landmarks = sliding_average.update(hand_landmarks.landmark)
            finger_angles = calculate_finger_angles(smoothed_landmarks)
            dic_angles = finger_angles[param]

            for clé, valeur in dic_angles.items():
                print(clé, valeur)
                
    img = Image.fromarray(rgb_frame)
    imgtk = ImageTk.PhotoImage(image=img)

    image_label.imgtk = imgtk
    image_label.configure(image=imgtk)

    image_label.after(10, update_frame)

# Démarrer la mise à jour de l'image
update_frame()

# Lancer la boucle principale Tkinter
root.mainloop()

# Arrêter la caméra à la fermeture de la fenêtre
picam2.stop()
