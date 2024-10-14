import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json
import numpy as np
from math import sqrt

# Initialisation de MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Utilisation de MediaPipe Drawing pour dessiner les points de repère
mp_drawing = mp.solutions.drawing_utils

# Ouvrir la webcam
cap = cv2.VideoCapture(0)  # Assure-toi que cette ligne est présente pour ouvrir la webcam

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
    plt.pause(0.001)  # Pause pour permettre à Matplotlib de rafraîchir

# Fonction pour calculer l'angle entre deux vecteurs dans un espace 3D
def calculate_angle(v1, v2):
    # Normaliser les vecteurs
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    
    # Calcul du produit scalaire
    dot_product = np.dot(v1, v2)
    
    # Calcul de l'angle en radians
    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))  # Clip pour éviter les erreurs numériques
    
    # Convertir en degrés
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

# Fonction pour calculer l'angle entre deux vecteurs dans un espace 3D
def calculate_angle(v1, v2):
    # Normaliser les vecteurs
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    
    # Calcul du produit scalaire
    dot_product = np.dot(v1, v2)
    
    # Calcul de l'angle en radians
    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))  # Clip pour éviter les erreurs numériques
    
    # Convertir en degrés
    angle_deg = np.degrees(angle_rad)
    
    return angle_deg

# Fonction pour calculer les angles de chaque phalange
def calculate_finger_angles(landmarks):
    angles = {}

    # Indices des landmarks pour chaque doigt
    finger_landmarks = {
        'pouce': [1, 2, 3, 4],          # Pouce (4 points)
        'index': [5, 6, 7, 8],          # Index (4 points)
        'majeur': [9, 10, 11, 12],      # Majeur (4 points)
        'annulaire': [13, 14, 15, 16],  # Annulaire (4 points)
        'auriculaire': [17, 18, 19, 20] # Auriculaire (4 points)
    }

    # Calcul des angles pour chaque doigt
    for finger_name, indices in finger_landmarks.items():
        angles[finger_name] = {}
        for i in range(1, len(indices) - 1):  # Calculer 3 angles pour chaque doigt
            start_idx = indices[i - 1]
            middle_idx = indices[i]
            end_idx = indices[i + 1]
            
            # Vecteurs des segments entre les points (dans l'espace 3D)
            v1 = np.array([landmarks[middle_idx].x - landmarks[start_idx].x,
                           landmarks[middle_idx].y - landmarks[start_idx].y,
                           landmarks[middle_idx].z - landmarks[start_idx].z])

            v2 = np.array([landmarks[end_idx].x - landmarks[middle_idx].x,
                           landmarks[end_idx].y - landmarks[middle_idx].y,
                           landmarks[end_idx].z - landmarks[middle_idx].z])

            # Calcul de l'angle de rotation
            angle = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_{i}'] = angle

    return angles


# Boucle principale pour traiter les images de la webcam
while cap.isOpened():  # Ici, cap doit être défini
    ret, frame = cap.read()
    
    if not ret:
        print("Erreur: Impossible de lire la vidéo.")
        break

    # Convertir l'image BGR (OpenCV) en RGB (MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Traiter l'image pour détecter les mains
    results = hands.process(rgb_frame)

    # Si des mains sont détectées
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            # Obtenir les coordonnées du poignet (point 0)
            wrist = hand_landmarks.landmark[0]
            wrist_coords = {'X': wrist.x, 'Y': wrist.y, 'Z': wrist.z}
            repère = hand_landmarks.landmark[17]
            normalisation = sqrt((wrist.x-repère.x)**2+(wrist.y-repère.y)**2+(wrist.z-repère.z)**2)

            # Calculer les coordonnées relatives par rapport au poignet
            keypoints_relative = []
            for i, data_point in enumerate(hand_landmarks.landmark):
                relative_x = data_point.x - wrist.x
                relative_y = data_point.y - wrist.y
                relative_z = data_point.z - wrist.z

                keypoints_relative.append({
                    'Index': i,   # L'index du point de repère
                    'Relative_X': relative_x/normalisation,
                    'Relative_Y': relative_y/normalisation,
                    'Relative_Z': relative_z/normalisation
                })
            
            # Récupérer les connexions des points de MediaPipe (connecteurs entre les articulations)
            connections = mp_hands.HAND_CONNECTIONS
            
            # Mettre à jour le tracé en 3D avec les points et leurs connexions
            update_plot(keypoints_relative, connections)

            # Calcul des angles pour les phalanges
            finger_angles = calculate_finger_angles(hand_landmarks.landmark)

            # Convertir les angles en JSON pour les visualiser
            angles_json = json.dumps(finger_angles, indent=4)
            print(angles_json)  # Affichage des angles dans le terminal

            # Dessiner les points de repère et les connexions sur l'image
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2, circle_radius=2)
            )

    # Afficher l'image avec les points de repère
    cv2.imshow('Détection des mains', frame)

    # Appuyer sur 'q' pour quitter la fenêtre
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
plt.close()
