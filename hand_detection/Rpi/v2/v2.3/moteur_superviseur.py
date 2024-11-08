
import time
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import pickle
import os
import time
import select
import sys
from biblio_init import *
from bibli_moteurs import *

def ecrire_stdout(string) :
	sys.stdout.write(string + "\n")
	sys.stdout.flush()
	
def ecrire_stderr(string) :
	sys.stderr.write(string + "\n")
	sys.stderr.flush()





#il reste à importer le nom de la fonction de régression pour convertir angle en commande moteur

#########################################
# 		VARIABLES		#
#########################################



moteurs = dict()
arti_to_moteurs = dict()
kits = list()
for i in range(5) :
	try :
		kits.append(MotorKit(i2c=board.I2C(), address=(0x60 + i)))
		for j in range(2) :
			moteur = eval(f"kits[{i}].stepper{j+1}")
			moteurs[moteur] = 0 
			arti_to_moteurs[index_to_arti(i,j)] = moteur
	except : pass

position_initiale = dict(moteurs)
for articulation in moteurs :
	position_initiale[articulation] = 0

print(arti_to_moteurs)

list_coeffs_doigts = charger_coeffs_doigts()



#########################################
# 		initiatilisation    	#
#########################################


ecrire_stdout("")


ecrire_stderr("Lecture de l'entrée standard (Ctrl+D pour arrêter) :")
for line in sys.stdin:
    temp_file_path = line.strip()
    ecrire_stderr("Reçu :" + str(temp_file_path))
    break

ecrire_stderr("initiatilisation terminée")


def steps_from_angle(angle):
        return newton_polynomial(angle, angles, coeffs)



with open(temp_file_path, "rb") as file :
	time.sleep(2)
	data = pickle.load(file)
	ecrire_stderr("data reconstitué :"+str(data))
	ecrire_stdout("c'est bon")
	ecrire_stderr("attente de données ...")
	#for line in sys.stdin :
	
	# attendre la première détection de main
	for line in sys.stdin:
		data = sys.stdin.readline().strip()
		with open(temp_file_path, "rb") as writen_file :
			data = pickle.load(writen_file)
		ecrire_stderr("data reconstitué :"+str(data))
		ecrire_stdout("c'est bon")
		break
	
#########################################
# 		BOUCLE			#
#########################################
	
	while True :
		
		if select.select([sys.stdin], [], [], 0.1)[0]:
			data = sys.stdin.readline().strip()
			with open(temp_file_path, "rb") as writen_file :
				data = pickle.load(writen_file)
			ecrire_stderr("data reconstitué :"+str(data))
			ecrire_stdout("c'est bon")

		doigt = "majeur"
		angles_doigt = data[doigt]
		angle1 = angles_doigt[doigt+"_angle_1"]
		angle2 = angles_doigt[doigt+"_angle_2"]
		
		commande = dict(moteurs)
		ecrire_stderr("--------------------------------------------------------------")
		ecrire_stderr(str(list_coeffs_doigts))
		commande[arti_to_moteurs["11"]] = int(newton_polynomial(angle1, list_coeffs_doigts["11"][0], list_coeffs_doigts["11"][1]))
		commande[arti_to_moteurs["12"]] = int(newton_polynomial(angle1, list_coeffs_doigts["12"][0], list_coeffs_doigts["12"][1]))
	
		update_moteurs(moteurs, commande)


			
