import socket
import threading
import bpy
import math

def start_server():
    serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serveur_socket.bind(('localhost', 12345))
    serveur_socket.listen(1)
    print("Le serveur est en écoute sur le port 12345...")

    connexion, adresse_client = serveur_socket.accept()
    print(f"Connexion établie avec {adresse_client}")
    
    while True:
        try:
            data = connexion.recv(1024).decode()
            if not data:
                print("Client déconnecté.")
                connexion.close()
                break
            
            print(f"Message reçu : {data}")
            
            # Split du message en liste d'angles
            angles = data.split(',')
            
            # Vérification que tous les angles sont bien des floats
            if len(angles) == 10 and all(is_float(value) for value in angles):  # 10 angles pour 5 doigts
                # Conversion des angles reçus en floats
                angles_floats = [float(angle) for angle in angles]

                # Mettre à jour l'armature avec ces angles dans le thread principal
                bpy.app.timers.register(lambda: update_armature(angles_floats))
                
            connexion.sendall("Message bien reçu".encode())

        except ConnectionResetError:
            print("La connexion a été interrompue.")
            connexion.close()
            break

def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def update_armature(angles):
    """
    Mettre à jour les angles des os dans l'armature Blender.
    angles : liste de 10 angles (2 par doigt)
    """
    armature = bpy.data.objects.get('Armature')  # Nom de l'armature dans Blender
    if armature and armature.type == 'ARMATURE':
        # S'assurer que l'armature est active
        bpy.context.view_layer.objects.active = armature
        armature.select_set(True)
        
        # Passer en mode Edit
        try:
            bpy.ops.object.mode_set(mode='EDIT')
            
            # Mise à jour des os dans l'armature
            try:
                # Appliquer les angles aux bons os (doigt par doigt)
                # Pouce
                armature.data.edit_bones['pouce1'].roll = math.radians(angles[0])
                armature.data.edit_bones['pouce2'].roll = math.radians(angles[1])
                # Index
                armature.data.edit_bones['index1'].roll = math.radians(angles[2])
                armature.data.edit_bones['index2'].roll = math.radians(angles[3])
                # Majeur
                armature.data.edit_bones['majeur1'].roll = math.radians(angles[4])
                armature.data.edit_bones['majeur2'].roll = math.radians(angles[5])
                # Annulaire
                armature.data.edit_bones['annulaire1'].roll = math.radians(angles[6])
                armature.data.edit_bones['annulaire2'].roll = math.radians(angles[7])
                # Auriculaire
                armature.data.edit_bones['auriculaire1'].roll = math.radians(angles[8])
                armature.data.edit_bones['auriculaire2'].roll = math.radians(angles[9])
            
            except KeyError as e:
                print(f"Erreur : Os {e} non trouvé dans l'armature. Vérifiez les noms des os dans Blender.")
        
        finally:
            # Sortir du mode édition et repasser en mode Objet
            bpy.ops.object.mode_set(mode='OBJECT')

def run_socket_in_thread():
    thread = threading.Thread(target=start_server)
    thread.daemon = True
    thread.start()

run_socket_in_thread()

print("Le serveur Blender est prêt.")
