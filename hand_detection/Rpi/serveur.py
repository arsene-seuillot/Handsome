import socket
import pickle

# Créer le socket serveur
serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur_socket.bind(('localhost', 12345))  # adresse et port du serveur
serveur_socket.listen(1)

print("Le serveur est en attente de connexion...")

conn, adresse = serveur_socket.accept()
print(f"Connexion reçue de {adresse}")

# Le serveur reçoit des données en continu
while True:
	data = conn.recv(4096)  # Taille en bytes à recevoir
	# Désérialiser le dictionnaire
	dictionnaire = pickle.loads(data)
	print("Dictionnaire reçu :", dictionnaire)

# Fermer la connexion
conn.close()
serveur_socket.close()
