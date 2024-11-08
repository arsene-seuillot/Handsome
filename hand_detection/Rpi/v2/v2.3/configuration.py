from biblio_init import *
from bibli_moteurs import *
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board



'''
kit0 = MotorKit(i2c=board.I2C(), address=0x60)
kit1 = MotorKit(i2c=board.I2C(), address=0x61)

'''

#dictionnnaire lien les données


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



while True :

	print("------ Coefficients connues --------")
	for doigt in list_coeffs_doigts :
		print("doigt : ", doigt)
	try : arti = int(input("Articulation à initialiser (0 pour passer) : "))
	except : print("Wrong input")
	
	if arti == 0 :
		break
	
	arti = str(arti)
	
	arti_to_moteurs[arti].release()
	input("Press enter when motors are well positionned")
	calibration_procedure(arti, moteurs, arti_to_moteurs)
	





'''

	for i in range(nb_doigts) :
		for j in range(2) :
			arti_to_moteurs[str(i+1) + str(j+1)].release()
			input("waiting to adjust motor ... ")
			calibration_procedure(str(i+1) + str(j+1), moteurs, arti_to_moteurs)
'''
def steps_from_angle(angle):
    return newton_polynomial(angle, angles, coeffs)



	
set_motors_commande(moteurs, position_initiale)
