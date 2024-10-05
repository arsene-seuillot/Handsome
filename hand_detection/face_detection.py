import cv2
import mediapipe as mp

# Initialiser MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh()

# Initialiser MediaPipe Drawing utils
mp_drawing = mp.solutions.drawing_utils

# Capturer la vidéo de la webcam
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    
    if not ret:
        print("Erreur: Impossible de lire la vidéo.")
        break

    # Convertir l'image BGR de OpenCV en RGB car MediaPipe utilise RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Traiter l'image pour détecter les points de repère
    results = face_mesh.process(rgb_frame)

    # Si des visages sont détectés
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Dessiner les points de repère faciaux sur l'image originale
            mp_drawing.draw_landmarks(
                frame, 
                face_landmarks, 
                mp_face_mesh.FACEMESH_TESSELATION,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=1, circle_radius=1),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=1)
            )

    # Afficher l'image
    cv2.imshow('Webcam', frame)

    # Appuyer sur 'q' pour quitter la fenêtre
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libérer les ressources
cap.release()
cv2.destroyAllWindows()
