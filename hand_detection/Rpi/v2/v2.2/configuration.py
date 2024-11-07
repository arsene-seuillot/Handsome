from biblio_init import *
from bibli_moteurs import *
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board




kit0 = MotorKit(i2c=board.I2C(), address=0x60)
kit1 = MotorKit(i2c=board.I2C(), address=0x61)

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
nb_doigts = 1









try :
	list_coeffs_doigts = []
	for i in range(nb_doigts) :
		list_coeffs_phalange = []
		for j in range(2) :
			list_coeffs_phalange.append(load_calibration_from_csv(str(i+1)+str(j+1)))
		list_coeffs_doigts.append(list_coeffs_phalange)

except :

	for i in range(nb_doigts) :
		for j in range(2) :
			doigts_to_moteurs[str(i+1) + str(j+1)].release()
			input("waiting to adjust motor ... ")
			calibration_procedure(str(i+1) + str(j+1), moteurs, doigts_to_moteurs)

def steps_from_angle(angle):
    return newton_polynomial(angle, angles, coeffs)






position_initiale = {	kit0.stepper1 : 0, kit0.stepper2 : 0, 
			kit1.stepper1 : 0, kit1.stepper2 : 0 
			#kit2.stepper1 : pas21, kit2.stepper2 : pas22,
			#kit3.stepper1 : pas31, kit3.stepper2 : pas32,
			#kit4.stepper1 : pas41, kit4.stepper2 : pas42 
			}

set_motors_commande(moteurs, position_initiale)
