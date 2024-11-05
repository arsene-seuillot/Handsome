
import time
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

#il reste à importer le nom de la fonction de régression pour convertir angle en commande moteur

#########################################
# 		VARIABLES		#
#########################################


#moteurs
kit0 = MotorKit(i2c=board.I2C(), address=0x60)
kit1 = MotorKit(i2c=board.I2C(), address=0x61)
kit2 = MotorKit(i2c=board.I2C(), address=0x62)
kit3 = MotorKit(i2c=board.I2C(), address=0x63)
kit4 = MotorKit(i2c=board.I2C(), address=0x64)

#allkit= MotorKit(i2c=board.I2C(), address=0x80)

#suivie de leur nombre de pas
pas0 = 0
pas1 = 0
pas2 = 0
pas3 = 0
pas4 = 0
pas5 = 0
pas6 = 0
pas7 = 0
pas8 = 0
pas9 = 0

#dictionnnaire lien les données
moteurs = {	kit0.stepper1 : pas01, kit0.stepper2 : pas02, 
		kit1.stepper1 : pas11, kit1.stepper2 : pas12, 
		kit2.stepper1 : pas21, kit2.stepper2 : pas22,
		kit3.stepper1 : pas31, kit3.stepper2 : pas32,
		kit4.stepper1 : pas41, kit4.stepper2 : pas42 }






#########################################
# 		BOUCLE			#
#########################################


boucle = True

while boucle :
# main loop
	
	
	angles = fonction_angle()  		#il faut ajouter la façon dont on récupère les information des degrès de commande
	commande = fonction_commande()  	# il faut adapter cette ligne avec le nom du fichier de la fonction regression
	
	
	
	for i,moteur in enumerate(moteurs) :
	
		ordre = 1
		if moteurs[moteur] > commande[i] :
			moteur.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
			moteurs[moteur] += 1
		elif moteurs[moteur] < commande[i] :
			moteur.onestep(direction = stepper.FORWARD, style = stepper.DOUBLE)
			moteurs[moteur] -= 1
		
	time.sleep(0.01)





			
