
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


#moteurs
kit0 = MotorKit(i2c=board.I2C(), address=0x60)
kit1 = MotorKit(i2c=board.I2C(), address=0x61)
#kit2 = MotorKit(i2c=board.I2C(), address=0x62)
#kit3 = MotorKit(i2c=board.I2C(), address=0x63)
#kit4 = MotorKit(i2c=board.I2C(), address=0x64)

#allkit= MotorKit(i2c=board.I2C(), address=0x80)

#suivie de leur nombre de pas
pas01 = 0
pas02 = 0
pas11 = 0
pas12 = 0
#pas21 = 0
#pas22 = 0
#pas31 = 0
#pas32 = 0
#pas41 = 0
#pas42 = 0

#dictionnnaire lien les données
moteurs = {	kit0.stepper1 : pas01, kit0.stepper2 : pas02, 
		kit1.stepper1 : pas11, kit1.stepper2 : pas12 
		#kit2.stepper1 : pas21, kit2.stepper2 : pas22,
		#kit3.stepper1 : pas31, kit3.stepper2 : pas32,
		#kit4.stepper1 : pas41, kit4.stepper2 : pas42 
		}
		
		
doigts_to_moteurs = { 	"11" : kit1.stepper1, "12" : kit0.stepper1,
			"21" : kit0.stepper2, "21" : kit1.stepper2
			}

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

list_coeffs_doigts = []
for i in range(1) :
	list_coeffs_phalange = []
	for j in range(2) :
		list_coeffs_phalange.append(load_calibration_from_csv(str(i+1)+str(j+1)))
	list_coeffs_doigts.append(list_coeffs_phalange)

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
		commande[doigts_to_moteurs["11"]] = int(newton_polynomial(angle1, list_coeffs_doigts[0][0][0], list_coeffs_doigts[0][0][1]))
		commande[doigts_to_moteurs["12"]] = int(newton_polynomial(angle1, list_coeffs_doigts[0][1][0], list_coeffs_doigts[0][1][1]))
	
		update_moteurs(moteurs, commande)


			
