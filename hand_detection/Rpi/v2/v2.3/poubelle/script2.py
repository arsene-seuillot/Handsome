import pickle
import os
import time
import select

#Remplacez `temp_file_path` par le chemin affiché par le Script 1
#temp_file_path = 'chemin_vers_fichier_temporaire'  # À remplacer

import sys

def ecrire_stdout(string) :
	sys.stdout.write(string + "\n")
	sys.stdout.flush()
	
def ecrire_stderr(string) :
	sys.stderr.write(string + "\n")
	sys.stderr.flush()


ecrire_stdout("")


ecrire_stderr("Lecture de l'entrée standard (Ctrl+D pour arrêter) :")
for line in sys.stdin:
    temp_file_path = line.strip()
    ecrire_stderr("Reçu :" + str(temp_file_path))
    break

ecrire_stderr("initiatilisation terminée")

with open(temp_file_path, "rb") as file :
	time.sleep(2)
	data = pickle.load(file)
	ecrire_stderr("data reconstitué :"+str(data))
	ecrire_stdout("c'est bon")
	ecrire_stderr("attente de données ...")
	#for line in sys.stdin :
	while True :
		if select.select([sys.stdin], [], [], 0.1)[0]:
			data = sys.stdin.readline().strip()
			with open(temp_file_path, "rb") as writen_file :
				data = pickle.load(writen_file)
			ecrire_stderr("data reconstitué :"+str(data))
			ecrire_stdout("c'est bon")


# Lire et désérialiser le dictionnaire depuis le fichier
#with open(temp_file_path, 'rb') as temp_file:
#    data_received = pickle.load(temp_file)

#print("Dictionnaire reçu :", data_received)
