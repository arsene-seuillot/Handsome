
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
kit1 = MotorKit(address=0x61)

for i in range(200) :
    #kit0.stepper1.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
    kit0.stepper2.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
    #kit1.stepper1.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
    #kit1.stepper2.onestep(direction = stepper.BACKWARD, style = stepper.DOUBLE)
    
    time.sleep(0.01)

