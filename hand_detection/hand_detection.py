import cv2
import mediapipe as mp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from math import sqrt
import socket
import time

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

# Paramètres de connexion au serveur
server_ip = 'localhost'
server_port = 12345

# Fonction pour créer une connexion au serveur
def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((server_ip, server_port))
            print("Connecté au serveur Blender")
            return client_socket
        except (ConnectionRefusedError, OSError):
            print("Impossible de se connecter au serveur, nouvelle tentative dans 3 secondes...")
            time.sleep(3)

# Connexion initiale
client_socket = connect_to_server()

# Fonction pour envoyer des données au serveur et gérer les erreurs
def send_angles_to_server(socket, angles_str):
    try:
        socket.sendall(angles_str.encode('utf-8'))
        print(f"Message envoyé : {angles_str}")
    except (BrokenPipeError, ConnectionResetError):
        print("Connexion perdue, tentative de reconnexion...")
        socket.close()
        socket = connect_to_server()
        socket.sendall(angles_str.encode('utf-8'))
        print(f"Message renvoyé après reconnexion : {angles_str}")
    return socket

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
    v1 = v1 / np.linalg.norm(v1)  # Normaliser le vecteur v1
    v2 = v2 / np.linalg.norm(v2)  # Normaliser le vecteur v2
    dot_product = np.dot(v1, v2)  # Calcul du produit scalaire
    angle_rad = np.arccos(np.clip(dot_product, -1.0, 1.0))  # Calcul de l'angle en radians
    return np.degrees(angle_rad)

# Fonction pour calculer les angles de chaque phalange
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
        for i in range(1, len(indices) - 1):
            start_idx = indices[i - 1]
            middle_idx = indices[i]
            end_idx = indices[i + 1]
            v1 = np.array([landmarks[middle_idx].x - landmarks[start_idx].x,
                           landmarks[middle_idx].y - landmarks[start_idx].y,
                           landmarks[middle_idx].z - landmarks[start_idx].z])

            v2 = np.array([landmarks[end_idx].x - landmarks[middle_idx].x,
                           landmarks[end_idx].y - landmarks[middle_idx].y,
                           landmarks[end_idx].z - landmarks[middle_idx].z])

            angle = calculate_angle(v1, v2)
            angles[finger_name][f'{finger_name}_angle_{i}'] = angle

    return angles

# Boucle principale pour traiter les images de la webcam et envoyer les angles au serveur
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
                normalisation = sqrt((wrist.x-repère.x)**2+(wrist.y-repère.y)**2+(wrist.z-repère.z)**2)

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

                finger_angles = calculate_finger_angles(hand_landmarks.landmark)

                angles_to_send = [
                    finger_angles['pouce']['pouce_angle_1'],
                    finger_angles['pouce']['pouce_angle_2'],
                    finger_angles['index']['index_angle_1'],
                    finger_angles['index']['index_angle_2'],
                    finger_angles['majeur']['majeur_angle_1'],
                    finger_angles['majeur']['majeur_angle_2'],
                    finger_angles['annulaire']['annulaire_angle_1'],
                    finger_angles['annulaire']['annulaire_angle_2'],
                    finger_angles['auriculaire']['auriculaire_angle_1'],
                    finger_angles['auriculaire']['auriculaire_angle_2']
                ]
                
                angles_str = ','.join([str(angle) for angle in angles_to_send])
                client_socket = send_angles_to_server(client_socket, angles_str)

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
    client_socket.close()
    plt.close()
