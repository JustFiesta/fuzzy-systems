import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

# zad4
print("zad 4: Sterownik hamowania na podstawie odległości")

# zm wej: odleglosc od najblizszego pojazdu [metry]
distance = ctrl.Antecedent(np.arange(0, 51, 1), 'distance')

# funckcje przynaleznosci
distance['BLISKI'] = fuzz.trapmf(distance.universe, [0, 0, 5, 15])
distance['ŚREDNI'] = fuzz.trimf(distance.universe, [10, 20, 30])
distance['DUŻY'] = fuzz.trapmf(distance.universe, [25, 35, 50, 50])
distance.view()

# zm wyj: sila hamowania [0-6]
braking = ctrl.Consequent(np.arange(0, 6.1, 0.1), 'braking')

# funkcje przynaleznosci hamowania
braking['BRAK'] = fuzz.trapmf(braking.universe, [0, 0, 0.5, 1.5])
braking['LEKKIE'] = fuzz.trimf(braking.universe, [1, 2.5, 4])
braking['MOCNE'] = fuzz.trapmf(braking.universe, [3, 4.5, 6, 6])
braking.view()

# reguly
rule1 = ctrl.Rule(distance['BLISKI'], braking['MOCNE'])
rule2 = ctrl.Rule(distance['ŚREDNI'], braking['LEKKIE'])
rule3 = ctrl.Rule(distance['DUŻY'], braking['BRAK'])

# sterownik + symulacja
braking_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
braking_sim = ctrl.ControlSystemSimulation(braking_ctrl)
braking_sim.input['distance'] = 12
braking_sim.compute()
print(f"zad4 - Wynik hamowania: {braking_sim.output['braking']:.2f}")
distance.view(sim=braking_sim)
braking.view(sim=braking_sim)
plt.show()

# zad5: zad4 + wilgotność nawierzchni
print("\nZad5: Dodanie wilgotności nawierzchni")

# Nowa zm wejsciowa: wilgotnosc [%]
humidity = ctrl.Antecedent(np.arange(0, 101, 1), 'humidity')
humidity['SUCHA'] = fuzz.trapmf(humidity.universe, [0, 0, 20, 40])
humidity['MOKRA'] = fuzz.trimf(humidity.universe, [30, 50, 70])
humidity['BARDZO_MOKRA'] = fuzz.trapmf(humidity.universe, [60, 80, 100, 100])
humidity.view()

# nowe reguly rozmyte dla wiglotnosci
rule4 = ctrl.Rule(distance['BLISKI'] & humidity['SUCHA'], braking['MOCNE'])
rule5 = ctrl.Rule(distance['BLISKI'] & humidity['MOKRA'], braking['MOCNE'])
rule6 = ctrl.Rule(distance['BLISKI'] & humidity['BARDZO_MOKRA'], braking['MOCNE'])
rule7 = ctrl.Rule(distance['ŚREDNI'] & humidity['SUCHA'], braking['LEKKIE'])
rule8 = ctrl.Rule(distance['ŚREDNI'] & humidity['MOKRA'], braking['LEKKIE'])
rule9 = ctrl.Rule(distance['ŚREDNI'] & humidity['BARDZO_MOKRA'], braking['MOCNE'])
rule10 = ctrl.Rule(distance['DUŻY'], braking['BRAK'])

# sterownik i symulacja
braking_ctrl2 = ctrl.ControlSystem([rule4, rule5, rule6, rule7, rule8, rule9, rule10])
braking_sim2 = ctrl.ControlSystemSimulation(braking_ctrl2)
braking_sim2.input['distance'] = 12
braking_sim2.input['humidity'] = 45
braking_sim2.compute()
print(f"zad5 - Wynik hamowania: {braking_sim2.output['braking']:.2f}")
humidity.view(sim=braking_sim2)
braking.view(sim=braking_sim2)
plt.show()

# zad6: zad5 + oblodzenie nawierzchni
print("\nZadanie 6: Dodanie oblodzenia nawierzchni")

# kolejna zm wejsciowa: oblodzenie [%]
ice = ctrl.Antecedent(np.arange(0, 101, 1), 'ice')
ice['BRAK'] = fuzz.trapmf(ice.universe, [0, 0, 10, 30])
ice['UMIARKOWANE'] = fuzz.trimf(ice.universe, [20, 50, 80])
ice['DUŻE'] = fuzz.trapmf(ice.universe, [70, 90, 100, 100])
ice.view()

# reguly dla oblodzenia
rule11 = ctrl.Rule(distance['BLISKI'] & ice['BRAK'], braking['MOCNE'])
rule12 = ctrl.Rule(distance['BLISKI'] & ice['UMIARKOWANE'], braking['MOCNE'])
rule13 = ctrl.Rule(distance['BLISKI'] & ice['DUŻE'], braking['MOCNE'])
rule14 = ctrl.Rule(distance['ŚREDNI'] & ice['BRAK'], braking['LEKKIE'])
rule15 = ctrl.Rule(distance['ŚREDNI'] & ice['UMIARKOWANE'], braking['MOCNE'])
rule16 = ctrl.Rule(distance['ŚREDNI'] & ice['DUŻE'], braking['MOCNE'])
rule17 = ctrl.Rule(distance['DUŻY'] & ice['BRAK'], braking['BRAK'])
rule18 = ctrl.Rule(distance['DUŻY'] & ice['UMIARKOWANE'], braking['LEKKIE'])
rule19 = ctrl.Rule(distance['DUŻY'] & ice['DUŻE'], braking['MOCNE'])

# sterownik i symulacja
braking_ctrl3 = ctrl.ControlSystem([rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19])
braking_sim3 = ctrl.ControlSystemSimulation(braking_ctrl3)
braking_sim3.input['distance'] = 12
braking_sim3.input['ice'] = 60
braking_sim3.compute()
print(f"zad66 - Wynik hamowania: {braking_sim3.output['braking']:.2f}")
ice.view(sim=braking_sim3)
braking.view(sim=braking_sim3)
plt.show()
