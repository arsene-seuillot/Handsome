import socket

# Créer un socket client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Se connecter au serveur (Blender)
client_socket.connect(('localhost', 12345))

# Envoyer plusieurs messages
try:
    while True:
        message = input("Entrez un message (ou tapez 'fin' pour terminer) : ")
        client_socket.sendall(message.encode())
        
        # Si le message est 'fin', terminer la connexion
        if message.lower() == 'fin':
            print("Fermeture de la connexion.")
            break
        
        # Recevoir la réponse du serveur
        reponse = client_socket.recv(1024).decode()
        print(f"Réponse du serveur : {reponse}")

finally:
    client_socket.close()
