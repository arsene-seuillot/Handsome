# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple test for using adafruit_motorkit with a stepper motor"""
import time
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit1 = MotorKit(i2c=board.I2C(), address=0x60)
#kit2 =0
kit2 = MotorKit(i2c=board.I2C(), address=0x61)
#allkit= MotorKit(i2c=board.I2C(), address=0x70)


boucle = True

while boucle :
	
	commande = int(input("mouvement : "))
	
	if commande == 0 :
		boucle = False
	
	elif commande == 1 :
		for i in range(200) :
			kit1.stepper1.onestep(direction = 1, style = 2)
			kit1.stepper2.onestep(direction = 1, style = 2)
	elif commande == 2 :
		for i in range(200) :
			kit2.stepper1.onestep(direction = 1, style = 2)
			kit2.stepper2.onestep(direction = 1, style = 2)
			
	
