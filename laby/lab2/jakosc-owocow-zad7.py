import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

print("zad7: Sterownik oceny jakości owoców")

# zm wej: SIZE - zakres 0-10
size = ctrl.Antecedent(np.arange(0, 10.1, 0.1), 'size')
# funkcje przyn dla rozmiaru
size['small'] = fuzz.trapmf(size.universe, [0, 0, 5, 10])  # malejąca od 1 do 0
size['large'] = fuzz.trapmf(size.universe, [0, 5, 10, 10])  # rosnąca od 0 do 1
size.view()
plt.title('Funkcje przynależności - ROZMIAR')

# zm wej: WEIGHT - zakres 0-100
weight = ctrl.Antecedent(np.arange(0, 101, 1), 'weight')
# funkcje przyn dla wagi
weight['small'] = fuzz.trapmf(weight.universe, [0, 0, 50, 100])  # malejąca od 1 do 0
weight['large'] = fuzz.trapmf(weight.universe, [0, 50, 100, 100])  # rosnąca od 0 do 1
weight.view()
plt.title('Funkcje przynależności - WAGA')

# zm wyj: QUALITY (jakość) - zakres 0-1
quality = ctrl.Consequent(np.arange(0, 1.01, 0.01), 'quality')
# funkcje przyn dla jakości
quality['bad'] = fuzz.trapmf(quality.universe, [0, 0, 0.5, 0.5])  # malejąca 1→0
quality['medium'] = fuzz.trimf(quality.universe, [0, 0.5, 1])     # trójkątna
quality['good'] = fuzz.trapmf(quality.universe, [0.5, 0.5, 1, 1]) # rosnąca 0→1
quality.view()
plt.title('Funkcje przynależności - JAKOŚĆ')

# reguly
rule1 = ctrl.Rule(size['small'] & weight['small'], quality['bad'])
rule2 = ctrl.Rule(size['small'] & weight['large'], quality['medium'])
rule3 = ctrl.Rule(size['large'] & weight['small'], quality['medium'])
rule4 = ctrl.Rule(size['large'] & weight['large'], quality['good'])

# sterownik rozmyty
fruit_quality_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
fruit_quality_sim = ctrl.ControlSystemSimulation(fruit_quality_ctrl)

# Testowanie sterownik
test_cases = [
    (2, 20),   # mały rozmiar, mała waga -> zła jakość
    (3, 80),   # mały rozmiar, duża waga -> średnia jakość
    (8, 30),   # duży rozmiar, mała waga -> średnia jakość
    (8, 85)    # duży rozmiar, duża waga -> dobra jakość
]

print("\nWyniki testowania sterownika:")
for i, (size_val, weight_val) in enumerate(test_cases, 1):
    fruit_quality_sim.input['size'] = size_val
    fruit_quality_sim.input['weight'] = weight_val
    fruit_quality_sim.compute()
    result = fruit_quality_sim.output['quality']

    # Określenie kategorii jakości na podstawie wyniku
    if result <= 0.33:
        category = "ZŁA"
    elif result <= 0.66:
        category = "ŚREDNIA"
    else:
        category = "DOBRA"

    print(f"Test {i}: Rozmiar={size_val}, Waga={weight_val} -> Jakość={result:.3f} ({category})")

# wizualizacja ostatniego testu
fruit_quality_sim.input['size'] = 8
fruit_quality_sim.input['weight'] = 85
fruit_quality_sim.compute()

plt.figure()
size.view(sim=fruit_quality_sim)
plt.title('Rozmiar owocu - aktywacja')

plt.figure()
weight.view(sim=fruit_quality_sim)
plt.title('Waga owocu - aktywacja')

plt.figure()
quality.view(sim=fruit_quality_sim)
plt.title('Ocena jakości - wynik')

plt.show()
