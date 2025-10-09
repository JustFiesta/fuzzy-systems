import numpy as np
import fuzzy as fuzz
from fuzzy import control as ctrl
import matplotlib.pyplot as plt

# zmienne wejściowe
quality_of_service = ctrl.Antecedent(np.arange(0, 11, 1), 'quality')
quality_of_food = ctrl.Antecedent(np.arange(0, 10, 1), 'food_quality')

# zmienna wyjściowa
tip = ctrl.Consequent(np.arange(0, 26, 1), 'tip')  # Zwiększyłem zakres do 25%

# funkcje przynależności do zmiennej wejściowej
quality_of_service['BAD'] = fuzz.trapmf(quality_of_service.universe, [0, 0, 3, 5])
quality_of_service['MEDIUM'] = fuzz.trimf(quality_of_service.universe, [3, 5, 7])  
quality_of_service['HIGH'] = fuzz.trapmf(quality_of_service.universe, [6, 7, 10, 10])

# funkcje przynależności do zmiennej wyjściowej
quality_of_food['BAD'] = fuzz.trapmf(quality_of_food.universe, [0, 0, 3, 5])
quality_of_food['MEDIUM'] = fuzz.trimf(quality_of_food.universe, [3, 5, 7])
quality_of_food['GOOD'] = fuzz.trapmf(quality_of_food.universe, [6, 7, 10, 10])
quality_of_food.view()


# reguły rozmyte

# zad3 obie zmienne z AND
rule1 = ctrl.Rule(quality_of_service['BAD'] & quality_of_food['POOR'], tip['LOW'])
rule2 = ctrl.Rule(quality_of_service['BAD'] & quality_of_food['GOOD'], tip['LOW'])
rule3 = ctrl.Rule(quality_of_service['BAD'] & quality_of_food['EXCELLENT'], tip['MEDIUM'])

rule4 = ctrl.Rule(quality_of_service['MEDIUM'] & quality_of_food['POOR'], tip['LOW']) 
rule5 = ctrl.Rule(quality_of_service['MEDIUM'] & quality_of_food['GOOD'], tip['MEDIUM'])
rule6 = ctrl.Rule(quality_of_service['MEDIUM'] & quality_of_food['EXCELLENT'], tip['HIGH'])

rule7 = ctrl.Rule(quality_of_service['HIGH'] & quality_of_food['POOR'], tip['MEDIUM'])
rule8 = ctrl.Rule(quality_of_service['HIGH'] & quality_of_food['GOOD'], tip['HIGH'])
rule9 = ctrl.Rule(quality_of_service['HIGH'] & quality_of_food['EXCELLENT'], tip['HIGH'])

# definiujemy sterownik rozmyty
# sterownik składa z reguł rozmytych
# ale same reguły składają się ze zdefiniowanych wcześniej
# wejść/wyjść
tipper_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])

# zad3 test sterownika
print("=== TEST STEROWNIKA ===")
tipper_simulation = ctrl.ControlSystemSimulation(tipper_ctrl)

test_cases = [
    (2, 2, "Zła obsługa + złe jedzenie"),
    (2, 7, "Zła obsługa + dobre jedzenie"),
    (5, 2, "Średnia obsługa + złe jedzenie"),
    (5, 5, "Średnia obsługa + średnie jedzenie"),
    (5, 7, "Średnia obsługa + dobre jedzenie"),
    (7, 2, "Dobra obsługa + złe jedzenie"),
    (7, 5, "Dobra obsługa + średnie jedzenie"),
    (7, 7, "Dobra obsługa + dobre jedzenie"),
    (6.5, 6.5, "Oba czynniki na poziomie 6.5")
]

for service_quality, food_quality, description in test_cases:
    # ustalamy wejście ostre (crisp)
    tipper_simulation.input['quality'] = service_quality
    tipper_simulation.input['food_quality'] = food_quality

    # fuzzyfikacja wejścia ostrego - zamiana go na wejście rozmyte
    # podstawienie rozmytego wejścia do reguł
    # odczytanie z reguł rozmytego wyjścia
    # defuzzyfikacja zmiennej wyjściowej
    tipper_simulation.compute()

    print(f"\n{description}")
    print(f"obsluga: {service_quality}, Jedzenie: {food_quality}")
    print(f"napiwek: {tipper_simulation.output['tip']:.2f}%")

# wizualizacja wybranego przypadku
print("============================================")
print("Wizualizacja dla: Obsługa=4.5, Jedzenie=6.0")
print("============================================")

# ustalamy wejście ostre (crisp)
tipper_simulation.input['quality'] = 4.5
tipper_simulation.input['food_quality'] = 6.0

# fuzzyfikacja wejścia ostrego - zamiana go na wejście rozmyte
# podstawienie rozmytego wejścia do reguł
# odczytanie z reguł rozmytego wyjścia
# defuzzyfikacja zmiennej wyjściowej
tipper_simulation.compute()

quality_of_service.view(sim=tipper_simulation)
quality_of_food.view(sim=tipper_simulation)
tip.view(sim=tipper_simulation)
print(f"\nObliczony napiwek: {tipper_simulation.output['tip']:.2f}%")

plt.show()
