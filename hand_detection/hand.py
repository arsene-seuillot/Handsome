# Détéction de la main, mais sans l'interface Blender

import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from math import sqrt

# Initialisation de MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Utilisation de MediaPipe Drawing pour dessiner les points de repère
mp_drawing = mp.solutions.drawing_utils

# Ouvrir la webcam
cap = cv2.VideoCapture(0)

# Initialisation de Matplotlib pour le tracé en 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Mettre à jour les limites des axes 3D
ax.set_xlim([-0.5, 0.5])
ax.set_ylim([-0.5, 0.5])
ax.set_zlim([-0.5, 0.5])

# Fonction pour mettre à jour les points et les connexions 3D dans Matplotlib
def update_plot(points, connections):
    ax.cla()  # Effacer la figure précédente
    # Tracer les points
    ax.scatter(
        [p['Relative_X'] for p in points], 
        [p['Relative_Z'] for p in points], 
        [-p['Relative_Y'] for p in points], 
        c='r', marker='o'
    )

    # Tracer les connexions
    for conn in connections:
        start_idx, end_idx = conn
        start_point = points[start_idx]
        end_point = points[end_idx]
        ax.plot(
            [start_point['Relative_X'], end_point['Relative_X']],
            [start_point['Relative_Z'], end_point['Relative_Z']],
            [-start_point['Relative_Y'], -end_point['Relative_Y']],
            'b-', linewidth=2
        )

    # Mettre à jour les limites des axes
    ax.set_xlim([-2, 2])
    ax.set_ylim([-2, 2])
    ax.set_zlim([-2, 2])
    plt.draw()
    plt.pause(0.001)

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
        
        # Si le doigt est le pouce, calcul de deux angles
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
            # Premier angle : entre 0-X et X-(X+1)
            v1 = np.array([landmarks[indices[0] - 4].x - landmarks[0].x,
                           landmarks[indices[0] - 4].y - landmarks[0].y,
                           landmarks[indices[0] - 4].z - landmarks[0].z])
            v2 = np.array([landmarks[indices[1]].x - landmarks[indices[0]].x,
                           landmarks[indices[1]].y - landmarks[indices[0]].y,
                           landmarks[indices[1]].z - landmarks[indices[0]].z])
            angle1 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_1'] = angle1

            # Deuxième angle : entre X-(X+1) et (X+1)-(X+2)
            v1 = np.array([landmarks[indices[1]].x - landmarks[indices[0]].x,
                           landmarks[indices[1]].y - landmarks[indices[0]].y,
                           landmarks[indices[1]].z - landmarks[indices[0]].z])
            v2 = np.array([landmarks[indices[2]].x - landmarks[indices[1]].x,
                           landmarks[indices[2]].y - landmarks[indices[1]].y,
                           landmarks[indices[2]].z - landmarks[indices[1]].z])
            angle2 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_2'] = angle2

            # Troisième angle : entre (X+1)-(X+2) et (X+2)-(X+3)
            v1 = np.array([landmarks[indices[2]].x - landmarks[indices[1]].x,
                           landmarks[indices[2]].y - landmarks[indices[1]].y,
                           landmarks[indices[2]].z - landmarks[indices[1]].z])
            v2 = np.array([landmarks[indices[3]].x - landmarks[indices[2]].x,
                           landmarks[indices[3]].y - landmarks[indices[2]].y,
                           landmarks[indices[3]].z - landmarks[indices[2]].z])
            angle3 = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_3'] = angle3

    return angles

# Boucle principale pour traiter les images de la webcam
try:
    while cap.isOpened():
        ret, frame = cap.read()
        
        if not ret:
            print("Erreur: Impossible de lire la vidéo.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                
                wrist = hand_landmarks.landmark[0]
                repère = hand_landmarks.landmark[17]
                # Calculer la distance de normalisation entre le poignet et le repère
                normalisation = sqrt((wrist.x - repère.x)**2 + (wrist.y - repère.y)**2 + (wrist.z - repère.z)**2)
                if normalisation < 1e-6:
                    normalisation = 1.0  # Pour éviter les divisions par 0

                keypoints_relative = []
                for i, data_point in enumerate(hand_landmarks.landmark):
                    relative_x = data_point.x - wrist.x
                    relative_y = data_point.y - wrist.y
                    relative_z = data_point.z - wrist.z

                    keypoints_relative.append({
                        'Index': i,
                        'Relative_X': relative_x/normalisation,
                        'Relative_Y': relative_y/normalisation,
                        'Relative_Z': relative_z/normalisation
                    })
                
                connections = mp_hands.HAND_CONNECTIONS
                update_plot(keypoints_relative, connections)

                # Calculer les angles des doigts
                finger_angles = calculate_finger_angles(hand_landmarks.landmark)
                print(finger_angles)

                mp_drawing.draw_landmarks(
                    frame, 
                    hand_landmarks, 
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
                )

        cv2.imshow('Détection des mains', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    cv2.destroyAllWindows()
    plt.close()
