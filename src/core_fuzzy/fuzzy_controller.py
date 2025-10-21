"""
Moduł sterowania rozmytego mocą silnika samochodu.

Implementuje logikę rozmytą do obliczania wartości przepustnicy (throttle)
na podstawie błędu prędkości i przyspieszenia.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt


class FuzzyThrottleController:
    """
    Kontroler rozmyty dla sterowania przepustnicą silnika.
    
    Wejścia:
        - speed_error: różnica między prędkością docelową a rzeczywistą [-30, 30]
        - acceleration: aktualne przyspieszenie pojazdu [-10, 10]
    
    Wyjście:
        - throttle: wartość przepustnicy [0, 100]
    """
    
    def __init__(self):
        """Inicjalizacja kontrolera - definiuje zmienne i reguły."""
        self._define_fuzzy_variables()
        self._define_membership_functions()
        self._define_rules()
        self._create_control_system()
    
    def _define_fuzzy_variables(self):
        """Definicja zmiennych lingwistycznych."""
        self.speed_error = ctrl.Antecedent(np.arange(-30, 31, 1), 'speed_error')
        self.acceleration = ctrl.Antecedent(np.arange(-10, 11, 1), 'acceleration')
        self.throttle = ctrl.Consequent(np.arange(0, 101, 1), 'throttle')
    
    def _define_membership_functions(self):
        """Definicja funkcji przynależności dla zmiennych lingwistycznych."""
        # Speed Error: negative (za szybko), zero (ok), positive (za wolno)
        self.speed_error['negative_large'] = fuzz.trapmf(
            self.speed_error.universe, [-30, -30, -20, -10]
        )
        self.speed_error['negative_small'] = fuzz.trimf(
            self.speed_error.universe, [-15, -5, 0]
        )
        self.speed_error['zero'] = fuzz.trimf(
            self.speed_error.universe, [-5, 0, 5]
        )
        self.speed_error['positive_small'] = fuzz.trimf(
            self.speed_error.universe, [0, 5, 15]
        )
        self.speed_error['positive_large'] = fuzz.trapmf(
            self.speed_error.universe, [10, 20, 30, 30]
        )
        
        # Acceleration: negative (zwalnianie), zero (stabilny), positive (przyspieszanie)
        self.acceleration['negative'] = fuzz.trapmf(
            self.acceleration.universe, [-10, -10, -5, 0]
        )
        self.acceleration['zero'] = fuzz.trimf(
            self.acceleration.universe, [-3, 0, 3]
        )
        self.acceleration['positive'] = fuzz.trapmf(
            self.acceleration.universe, [0, 5, 10, 10]
        )
        
        # Throttle: bardzo niski, niski, średni, wysoki, bardzo wysoki
        self.throttle['very_low'] = fuzz.trapmf(
            self.throttle.universe, [0, 0, 10, 20]
        )
        self.throttle['low'] = fuzz.trimf(
            self.throttle.universe, [10, 25, 40]
        )
        self.throttle['medium'] = fuzz.trimf(
            self.throttle.universe, [30, 50, 70]
        )
        self.throttle['high'] = fuzz.trimf(
            self.throttle.universe, [60, 75, 90]
        )
        self.throttle['very_high'] = fuzz.trapmf(
            self.throttle.universe, [80, 90, 100, 100]
        )
    
    def _define_rules(self):
        """Definicja reguł wnioskowania rozmytego (IF-THEN)."""
        self.rules = [
            # Gdy jesteśmy za szybko (negative error) - redukuj moc
            ctrl.Rule(
                self.speed_error['negative_large'],
                self.throttle['very_low']
            ),
            ctrl.Rule(
                self.speed_error['negative_small'] & self.acceleration['negative'],
                self.throttle['very_low']
            ),
            ctrl.Rule(
                self.speed_error['negative_small'] & self.acceleration['zero'],
                self.throttle['low']
            ),
            ctrl.Rule(
                self.speed_error['negative_small'] & self.acceleration['positive'],
                self.throttle['medium']
            ),
            
            # Gdy prędkość jest OK - utrzymuj
            ctrl.Rule(
                self.speed_error['zero'] & self.acceleration['negative'],
                self.throttle['low']
            ),
            ctrl.Rule(
                self.speed_error['zero'] & self.acceleration['zero'],
                self.throttle['medium']
            ),
            ctrl.Rule(
                self.speed_error['zero'] & self.acceleration['positive'],
                self.throttle['medium']
            ),
            
            # Gdy jesteśmy za wolno (positive error) - zwiększ moc
            ctrl.Rule(
                self.speed_error['positive_small'] & self.acceleration['negative'],
                self.throttle['medium']
            ),
            ctrl.Rule(
                self.speed_error['positive_small'] & self.acceleration['zero'],
                self.throttle['high']
            ),
            ctrl.Rule(
                self.speed_error['positive_small'] & self.acceleration['positive'],
                self.throttle['medium']
            ),
            
            # Duży błąd pozytywny - maksymalne przyspieszenie
            ctrl.Rule(
                self.speed_error['positive_large'] & self.acceleration['negative'],
                self.throttle['very_high']
            ),
            ctrl.Rule(
                self.speed_error['positive_large'] & 
                (self.acceleration['zero'] | self.acceleration['positive']),
                self.throttle['very_high']
            ),
        ]
    
    def _create_control_system(self):
        """Utworzenie systemu sterowania i symulatora."""
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control_system)
    
    def compute_throttle(self, speed_error: float, acceleration: float) -> float:
        """
        Oblicza wartość przepustnicy na podstawie błędu prędkości i przyspieszenia.
        
        Args:
            speed_error: różnica prędkości [-30, 30]
            acceleration: przyspieszenie [-10, 10]
        
        Returns:
            throttle: wartość przepustnicy [0, 100]
        """
        # Ograniczenie wartości wejściowych do zdefiniowanych zakresów
        speed_error = np.clip(speed_error, -30, 30)
        acceleration = np.clip(acceleration, -10, 10)
        
        # Ustawienie wejść
        self.simulator.input['speed_error'] = speed_error
        self.simulator.input['acceleration'] = acceleration
        
        # Wnioskowanie i defuzyfikacja (centroid)
        self.simulator.compute()
        
        return float(self.simulator.output['throttle'])
    
    def plot_memberships(self):
        """Wizualizacja funkcji przynależności dla wszystkich zmiennych."""
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # Speed Error
        self.speed_error.view(ax=axes[0])
        axes[0].set_title('Funkcje przynależności: Speed Error', fontsize=14, fontweight='bold')
        axes[0].set_xlabel('Speed Error [km/h]')
        axes[0].set_ylabel('Stopień przynależności')
        axes[0].grid(True, alpha=0.3)
        axes[0].legend(loc='upper right', fontsize=9)
        
        # Acceleration
        self.acceleration.view(ax=axes[1])
        axes[1].set_title('Funkcje przynależności: Acceleration', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Acceleration [m/s²]')
        axes[1].set_ylabel('Stopień przynależności')
        axes[1].grid(True, alpha=0.3)
        axes[1].legend(loc='upper right', fontsize=9)
        
        # Throttle
        self.throttle.view(ax=axes[2])
        axes[2].set_title('Funkcje przynależności: Throttle', fontsize=14, fontweight='bold')
        axes[2].set_xlabel('Throttle [%]')
        axes[2].set_ylabel('Stopień przynależności')
        axes[2].grid(True, alpha=0.3)
        axes[2].legend(loc='upper right', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def plot_control_surface(self):
        """Wizualizacja powierzchni sterowania (throttle vs speed_error vs acceleration)."""
        # Generowanie siatki punktów
        x = np.arange(-30, 31, 2)
        y = np.arange(-10, 11, 1)
        X, Y = np.meshgrid(x, y)
        Z = np.zeros_like(X, dtype=float)
        
        # Obliczenie throttle dla każdego punktu
        for i in range(X.shape[0]):
            for j in range(X.shape[1]):
                Z[i, j] = self.compute_throttle(X[i, j], Y[i, j])
        
        # Wizualizacja 3D
        fig = plt.figure(figsize=(14, 6))
        
        # Surface plot
        ax1 = fig.add_subplot(121, projection='3d')
        surf = ax1.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        ax1.set_xlabel('Speed Error [km/h]')
        ax1.set_ylabel('Acceleration [m/s²]')
        ax1.set_zlabel('Throttle [%]')
        ax1.set_title('Powierzchnia sterowania 3D', fontweight='bold')
        fig.colorbar(surf, ax=ax1, shrink=0.5)
        
        # Contour plot
        ax2 = fig.add_subplot(122)
        contour = ax2.contourf(X, Y, Z, levels=15, cmap='viridis')
        ax2.set_xlabel('Speed Error [km/h]')
        ax2.set_ylabel('Acceleration [m/s²]')
        ax2.set_title('Mapa konturowa sterowania', fontweight='bold')
        fig.colorbar(contour, ax=ax2, label='Throttle [%]')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


def run_simulation_examples():
    """Przykłady użycia kontrolera w różnych scenariuszach."""
    controller = FuzzyThrottleController()
    
    print("=" * 70)
    print(" SYMULACJA STEROWANIA ROZMYTEGO PRZEPUSTNICĄ SILNIKA")
    print("=" * 70)
    print()
    
    # Scenariusze testowe
    test_cases = [
        (-25, -5, "Dużo za szybko, zwalniamy"),
        (-10, 0, "Trochę za szybko, stabilne przyspieszenie"),
        (-5, 3, "Lekko za szybko, ale przyspieszamy"),
        (0, 0, "Idealna prędkość, stabilny ruch"),
        (5, -2, "Lekko za wolno, zwalniamy"),
        (10, 0, "Za wolno, stabilne przyspieszenie"),
        (20, 5, "Dużo za wolno, już przyspieszamy"),
        (25, -3, "Bardzo za wolno, ale zwalniamy"),
    ]
    
    results = []
    
    print(f"{'Scenario':<40} {'Error':<10} {'Accel':<10} {'Throttle':<10}")
    print("-" * 70)
    
    for error, accel, description in test_cases:
        throttle = controller.compute_throttle(error, accel)
        results.append((error, accel, throttle))
        print(f"{description:<40} {error:>6.1f} km/h {accel:>6.1f} m/s² {throttle:>6.1f} %")
    
    print()
    print("=" * 70)
    
    # Wykres wyników
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    errors = [r[0] for r in results]
    accels = [r[1] for r in results]
    throttles = [r[2] for r in results]
    
    # Throttle vs Speed Error
    ax1.plot(errors, throttles, 'o-', linewidth=2, markersize=8, color='royalblue')
    ax1.set_xlabel('Speed Error [km/h]', fontsize=12)
    ax1.set_ylabel('Throttle [%]', fontsize=12)
    ax1.set_title('Throttle vs Speed Error', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.axhline(y=50, color='r', linestyle='--', alpha=0.5, label='50% throttle')
    ax1.axvline(x=0, color='g', linestyle='--', alpha=0.5, label='zero error')
    ax1.legend()
    
    # Scatter: Error vs Acceleration (kolor = Throttle)
    scatter = ax2.scatter(errors, accels, c=throttles, s=200, cmap='RdYlGn', 
                          edgecolors='black', linewidth=1.5)
    ax2.set_xlabel('Speed Error [km/h]', fontsize=12)
    ax2.set_ylabel('Acceleration [m/s²]', fontsize=12)
    ax2.set_title('Mapa decyzji (kolor = Throttle)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
    ax2.axvline(x=0, color='gray', linestyle='-', alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax2)
    cbar.set_label('Throttle [%]', fontsize=10)
    
    plt.tight_layout()
    plt.show()


# ============================================================================
# PRZYKŁAD UŻYCIA
# ============================================================================

if __name__ == "__main__":
    # Utworzenie kontrolera
    controller = FuzzyThrottleController()
    
    # Test pojedynczego wywołania
    print("\nTest pojedynczego wywołania:")
    print("-" * 50)
    speed_err = 15.0
    accel = -2.0
    throttle = controller.compute_throttle(speed_err, accel)
    print(f"Speed Error: {speed_err} km/h")
    print(f"Acceleration: {accel} m/s²")
    print(f"→ Throttle: {throttle:.2f}%")
    print()
    
    # Uruchomienie pełnej symulacji
    run_simulation_examples()
    
    # Wizualizacja funkcji przynależności
    print("\nWyświetlanie funkcji przynależności...")
    controller.plot_memberships()
    
    # Wizualizacja powierzchni sterowania
    print("\nGenerowanie powierzchni sterowania...")
    controller.plot_control_surface()
    
    print("\n" + "=" * 70)
    print(" SYMULACJA ZAKOŃCZONA")
    print("=" * 70)
