import socket
import threading
import bpy
import math

# Fonction pour démarrer le serveur socket
def start_server():
    serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur_socket.bind(('localhost', 12345))
    serveur_socket.listen(1)
    print("Le serveur est en écoute sur le port 12345...")

    connexion, adresse_client = serveur_socket.accept()
    print(f"Connexion établie avec {adresse_client}")
    
    while True:
        try:
            # Recevoir des données
            data = connexion.recv(1024).decode()
            
            if not data:  # Si data est vide, cela signifie que la connexion est fermée
                print("Client déconnecté.")
                connexion.close()
                break
            
            # Traitement des données
            angles = data.split(',')
            

            if all(is_float(value) for value in angles):
                print("Toutes les valeurs sont des nombres flottants ou valides.")
            else:
                print("Certaines valeurs ne sont pas des nombres.")

            
            if len(angles) == 3:  # Supposons que nous recevons des angles pour trois os
                # Convertir les angles de chaîne à flottants
                try:
                    bone1_angle = float(angles[0])
                    bone2_angle = float(angles[1])
                    bone3_angle = float(angles[2])
                except ValueError:
                    print("Erreur : Les angles doivent être des nombres valides.")
                    continue
                
                # Mettre à jour les angles d'os dans l'armature
                update_armature(bone1_angle, bone2_angle, bone3_angle)

            # Répondre un message générique au client
            connexion.sendall("Angles reçus et appliqués".encode())

        except ConnectionResetError:
            print("La connexion a été interrompue.")
            connexion.close()
            break
        
        
def is_float(value):
    try:
        float(value)  # Essaye de convertir en float
        print(float(value))
        return True
    except ValueError:
        return False


# Fonction pour mettre à jour l'armature
def update_armature(bone1_angle, bone2_angle, bone3_angle):
    armature = bpy.data.objects.get('Armature')  # Nom de l'armature
    if armature and armature.type == 'ARMATURE':
        bpy.context.view_layer.objects.active = armature
        bpy.ops.object.mode_set(mode='EDIT')
        
        # Ajuster la rotation des os (en radians)
        armature.data.edit_bones['Bone.001'].roll = math.radians(bone1_angle)  # Exemple d'os
        armature.data.edit_bones['Bone.002'].roll = math.radians(bone2_angle)  # Exemple d'os
        armature.data.edit_bones['Bone.003'].roll = math.radians(bone3_angle)  # Exemple d'os
        
        bpy.ops.object.mode_set(mode='OBJECT')

# Lancer le serveur dans un thread séparé
def run_socket_in_thread():
    thread = threading.Thread(target=start_server)
    thread.daemon = True  # Le thread se ferme quand Blender s'arrête
    thread.start()

# Appeler la fonction pour démarrer le serveur dans un thread
run_socket_in_thread()

print("Le script Blender a démarré le serveur socket dans un thread séparé.")
