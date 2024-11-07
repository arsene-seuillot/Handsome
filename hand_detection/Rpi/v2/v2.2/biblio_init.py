import numpy as np
import csv
from bibli_moteurs import *



def newton_coeficients(steps, angles) :
    n = len(angles)
    coeffs = np.copy(steps).astype(float)

    for j in range(1,n):
        for i in range(n-1, j-1, -1):
            coeffs[i] = (coeffs[i] - coeffs[i - 1]) / (angles[i] - angles[i - j])
    return coeffs

def save_calibration_to_csv(coeffs, angles, doigt) :
    with open("coefficients/doigt" + doigt + ".csv", mode='w') as file :
        writer = csv.writer(file)
        writer.writerow(angles)
        writer.writerow(coeffs)

def load_calibration_from_csv(doigt):
    with open("coefficients/doigt" + doigt + ".csv", mode='r') as file :
        reader = csv.reader(file)
        angles = next(reader)
        coeffs = next(reader)
        angles = [float(a) for a in angles]
        coeffs = [float(c) for c in coeffs]
        return angles, coeffs


def newton_polynomial(x, angles, coeffs) :
    n = len(coeffs)
    result = coeffs[n-1]
    for i in range(n-2, -1,-1):
        result = result * (x - angles[i]) + coeffs[i]
    return result


def calibration_procedure(doigt, moteurs, doigts_to_moteurs):
    steps_list = []
    angles_list = []

    print("=== Procédure d'initialisation ===")
    print("Déplacez le moteur à différentes position, mesurez l'angle et entrez les valeurs.")
    print("Lorsque vous avez fini, entrez 'done'.")

    while True :
        try:
            steps = input("Entrez le nombre de pas pour la position (ou 'done' pour finir) : ")
            if steps.lower() == 'done':
                break
            steps = int(steps)
            
            commande = dict(moteurs)
            commande[doigts_to_moteurs[doigt]] = steps
            

            set_motors_commande(moteurs, commande)

            angle = float(input("Entrez l'angle mesuré (en degrés) pour cette position : "))

            steps_list.append(steps)
            angles_list.append(angle)

        except ValueError:
            print("Entrée invalide.")


    if len(steps_list) >= 2:
        coeffs = newton_coeficients(steps_list, angles_list)

        save_calibration_to_csv(coeffs, angles_list, doigt)
        print("Calibration terminée. Les angles et coefficients ont été enregistrés dans coefficients.csv")

        def steps_from_angle(angle):
            return newton_polynomial(angles, steps_list, coeffs)

        return steps_from_angle

    else:
        print("Erreur : Il faut au moins deux points pour la calibration.")
        return None
        


#angle_from_steps_function = calibration_procedure(doigt)

def exemple_usage():
    angles, coeffs = load_calibration_from_csv()

    def steps_from_angle(angle):
        return newton_polynomial(angle, angles, coeffs)

    test_angle = 45
    estimated_steps = steps_from_angle(test_angle)
    print(f"Pour {test_angle} degrés, le nombre de pas estimé est : {estimated_steps:.f}")
