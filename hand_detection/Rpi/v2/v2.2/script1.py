import pickle 
import tempfile 
import time 
import sys
import os

# Dictionnaire à envoyer
data = {'clé1': 'valeur1', 'clé2': 'valeur2', 'nombre': 123}
# Crée un fichier temporaire pour stocker le dictionnaire
with tempfile.NamedTemporaryFile(delete=True) as temp_file:
    # Sérialiser et écrire dans le fichier
    pickle.dump(data, temp_file)
    temp_file_path = temp_file.name  # On garde le chemin pour le script 2
    
    sys.stdout.write(temp_file_path + "\n")
    sys.stdout.flush()
    time.sleep(1)
time.sleep(5)
#print(f"Le dictionnaire a été écrit dans le fichier temporaire : {temp_file_path}")
