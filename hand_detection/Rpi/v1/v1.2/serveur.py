import socket
import pickle
import subprocess
import threading

# Fonction pour lancer le script de calcul et envoyer les résultats
def gestion_client():
	# Lancer le script de calcul en tant que sous-processus
	process = subprocess.Popen(["python3", "hand_rpi.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	# Attente d'une connexion client
	print("Le serveur est en attente de connexion...")
	conn, adresse = serveur_socket.accept()
	print(f"Connexion reçue de {adresse}")
    
	# Lire les données produites par le script et les envoyer au client
	try:
		for ligne in process.stdout:
			print(conn.recv(4096))
			print('hehehehe')
			data = conn.recv(4096)
			dictionnaire = pickle.loads(data)
			print("Dictionnaire reçu :", dictionnaire)
            
	except BrokenPipeError:
		print("Connexion fermée par le client.")
        
	finally:
		# Assurer la fermeture propre du sous-processus et de la connexion
		process.terminate()
		conn.close()
		print("Connexion client fermée.")

# Création du socket serveur
serveur_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serveur_socket.bind(('localhost', 12345))  # adresse et port du serveur
serveur_socket.listen(1)


# Lancer le calcul et envoyer les données dans un thread
thread_calcul = threading.Thread(target=gestion_client, args=())
thread_calcul.start()
# Attendre la fin du thread pour fermer le serveur
thread_calcul.join()

# Fermer le socket serveur
serveur_socket.close()
print("Serveur arrêté.")


