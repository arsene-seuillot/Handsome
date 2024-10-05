import socket

# Créer un socket TCP
serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Lier le socket à une adresse et un port
adresse_serveur = ('localhost', 12345)
serveur_socket.bind(adresse_serveur)

# Écouter les connexions entrantes
serveur_socket.listen(1)
print(f"Le serveur est en écoute sur {adresse_serveur}...")

# Accepter une connexion
connexion, adresse_client = serveur_socket.accept()
print(f"Connexion établie avec {adresse_client}")

while True:
    # Recevoir les données du client
    data = connexion.recv(1024).decode()

    # Si le client envoie 'fin', arrêter la boucle
    if data.lower() == 'fin':
        print("Le client a terminé la connexion.")
        connexion.sendall(b'Connexion terminee')
        break
    
    # Afficher et répondre au message
    print(f"Reçu : {data}")
    connexion.sendall(b'Reponse du serveur : Message recu')

# Fermer la connexion
connexion.close()
