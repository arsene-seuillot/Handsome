import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

def update_moteurs(moteurs, commande) :
	static = True
	for i,moteur in enumerate(moteurs) :
		if moteurs[moteur] > commande[moteur] :
			moteur.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
			moteurs[moteur] -= 1
			static = False
		elif moteurs[moteur] < commande[moteur] :
			moteur.onestep(direction = stepper.FORWARD, style = stepper.DOUBLE)
			moteurs[moteur] += 1
			static = False
		
		time.sleep(0.001)
	
	
	return static


def set_motors_commande(moteurs, commande) :

	static = False
	while not(static) :	
		static = update_moteurs(moteurs, commande)
