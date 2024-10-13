import socket
import threading
import bpy

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
            
            # Afficher les données reçues
            print(f"Reçu : {data}")

            # Répondre un message générique au client
            connexion.sendall("Message reçu".encode())

        except ConnectionResetError:
            print("La connexion a été interrompue.")
            connexion.close()
            break

# Lancer le serveur dans un thread séparé
def run_socket_in_thread():
    thread = threading.Thread(target=start_server)
    thread.daemon = True  # Le thread se ferme quand Blender s'arrête
    thread.start()

# Appeler la fonction pour démarrer le serveur dans un thread
run_socket_in_thread()

print("Le script Blender a démarré le serveur socket dans un thread séparé.")



