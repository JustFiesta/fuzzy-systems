"""
Moduł symulacji fizyki pojazdu dla fuzzy kontrolera.
Model dynamiki pojazdu w czasie dyskretnym.
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Tuple


class CarSimulation:
    """
    Symulator dynamiki pojazdu w 2D (ruch jednowymiarowy).
    
    Parametry:
        mass (float): Masa pojazdu [kg]
        drag_coeff (float): Współczynnik oporu [N·s/m]
        max_throttle (float): Maksymalna siła napędowa [N]
        dt (float): Krok czasowy symulacji [s]
    """
    
    def __init__(
        self,
        mass: float = 1000.0,
        drag_coeff: float = 50.0,
        max_throttle: float = 5000.0,
        dt: float = 0.033
    ):
        self.mass = mass
        self.drag_coeff = drag_coeff
        self.max_throttle = max_throttle
        self.dt = dt
        
        # Stan pojazdu
        self.position = 0.0
        self.speed = 0.0
        self.acceleration = 0.0
        
        # Historia (dla wizualizacji)
        self.history = {
            'time': [],
            'position': [],
            'speed': [],
            'acceleration': [],
            'throttle': []
        }
        
    def reset(self) -> None:
        """Resetuje stan pojazdu do wartości początkowych."""
        self.position = 0.0
        self.speed = 0.0
        self.acceleration = 0.0
        self.history = {
            'time': [],
            'position': [],
            'speed': [],
            'acceleration': [],
            'throttle': []
        }
        
    def update(self, throttle: float, dt: float = None) -> Dict[str, float]:
        """
        Aktualizuje stan pojazdu na podstawie wejścia throttle.
        
        Model fizyczny:
            F_net = F_throttle - F_drag
            F_drag = drag_coeff * speed
            acceleration = F_net / mass
            speed += acceleration * dt
            position += speed * dt
        
        Args:
            throttle: Wartość przepustnicy [0-100] (procent mocy)
            dt: Krok czasowy [s], jeśli None używa self.dt
            
        Returns:
            dict: Aktualny stan pojazdu
        """
        if dt is None:
            dt = self.dt
            
        # Ograniczenie throttle do zakresu [0, 100]
        throttle = np.clip(throttle, 0, 100)
        
        # Przeliczenie throttle na siłę [N]
        throttle_force = (throttle / 100.0) * self.max_throttle
        
        # Siła oporu
        drag_force = self.drag_coeff * self.speed
        
        # Obliczenie przyspieszenia
        net_force = throttle_force - drag_force
        self.acceleration = net_force / self.mass
        
        # Aktualizacja prędkości (nie może być ujemna)
        self.speed += self.acceleration * dt
        self.speed = max(0.0, self.speed)
        
        # Aktualizacja pozycji
        self.position += self.speed * dt
        
        # Stan do zwrócenia
        state = {
            'position': self.position,
            'speed': self.speed,
            'acceleration': self.acceleration,
            'throttle': throttle
        }
        
        return state
    
    def record_state(self, time: float, throttle: float) -> None:
        """Zapisuje aktualny stan do historii."""
        self.history['time'].append(time)
        self.history['position'].append(self.position)
        self.history['speed'].append(self.speed)
        self.history['acceleration'].append(self.acceleration)
        self.history['throttle'].append(throttle)
        
    def get_state(self) -> Dict[str, float]:
        """Zwraca aktualny stan pojazdu."""
        return {
            'position': self.position,
            'speed': self.speed,
            'acceleration': self.acceleration
        }
        
    def plot_results(self, title: str = "Symulacja pojazdu") -> None:
        """Wizualizuje wyniki symulacji."""
        if not self.history['time']:
            print("Brak danych do wizualizacji. Uruchom symulację.")
            return
            
        fig, axes = plt.subplots(4, 1, figsize=(10, 10))
        fig.suptitle(title, fontsize=14, fontweight='bold')
        
        time = self.history['time']
        
        # Wykres pozycji
        axes[0].plot(time, self.history['position'], 'b-', linewidth=2)
        axes[0].set_ylabel('Pozycja [m]', fontsize=10)
        axes[0].grid(True, alpha=0.3)
        axes[0].set_title('Pozycja w czasie')
        
        # Wykres prędkości
        axes[1].plot(time, self.history['speed'], 'r-', linewidth=2)
        axes[1].set_ylabel('Prędkość [m/s]', fontsize=10)
        axes[1].grid(True, alpha=0.3)
        axes[1].set_title('Prędkość w czasie')
        
        # Wykres przyspieszenia
        axes[2].plot(time, self.history['acceleration'], 'g-', linewidth=2)
        axes[2].set_ylabel('Przyspieszenie [m/s²]', fontsize=10)
        axes[2].grid(True, alpha=0.3)
        axes[2].set_title('Przyspieszenie w czasie')
        
        # Wykres throttle
        axes[3].plot(time, self.history['throttle'], 'm-', linewidth=2)
        axes[3].set_ylabel('Throttle [%]', fontsize=10)
        axes[3].set_xlabel('Czas [s]', fontsize=10)
        axes[3].grid(True, alpha=0.3)
        axes[3].set_title('Wejście sterujące')
        
        plt.tight_layout()
        plt.show()


def test_constant_throttle(throttle_value: float = 50.0, duration: float = 20.0):
    """
    Test symulacji ze stałym throttle.
    
    Args:
        throttle_value: Wartość przepustnicy [%]
        duration: Czas symulacji [s]
    """
    print(f"\n{'='*60}")
    print(f"TEST SYMULACJI: Throttle = {throttle_value}%")
    print(f"{'='*60}\n")
    
    # Inicjalizacja symulacji
    car = CarSimulation(
        mass=1000.0,
        drag_coeff=50.0,
        max_throttle=5000.0,
        dt=0.1
    )
    
    print(f"Parametry pojazdu:")
    print(f"  Masa: {car.mass} kg")
    print(f"  Współczynnik oporu: {car.drag_coeff} N·s/m")
    print(f"  Maksymalna siła: {car.max_throttle} N")
    print(f"  Krok czasowy: {car.dt} s")
    print(f"\nRozpoczynanie symulacji na {duration} sekund...\n")
    
    # Symulacja
    current_time = 0.0
    while current_time <= duration:
        state = car.update(throttle_value)
        car.record_state(current_time, throttle_value)
        current_time += car.dt
    
    # Wyniki końcowe
    final_state = car.get_state()
    print(f"Wyniki końcowe (t = {duration} s):")
    print(f"  Pozycja: {final_state['position']:.2f} m")
    print(f"  Prędkość: {final_state['speed']:.2f} m/s ({final_state['speed']*3.6:.2f} km/h)")
    print(f"  Przyspieszenie: {final_state['acceleration']:.2f} m/s²")
    
    # Prędkość maksymalna teoretyczna (v_max = F_throttle / drag_coeff)
    v_max_theory = (throttle_value/100.0) * car.max_throttle / car.drag_coeff
    print(f"\nPrędkość maksymalna (teoretyczna): {v_max_theory:.2f} m/s ({v_max_theory*3.6:.2f} km/h)")
    print(f"Osiągnięto: {(final_state['speed']/v_max_theory)*100:.1f}% prędkości maksymalnej")
    
    # Wizualizacja
    car.plot_results(f"Test symulacji: Throttle = {throttle_value}%")
    
    return car


def test_variable_throttle():
    """Test symulacji ze zmiennym throttle (przyspieszanie i hamowanie)."""
    print(f"\n{'='*60}")
    print(f"TEST SYMULACJI: Zmienny throttle")
    print(f"{'='*60}\n")
    
    car = CarSimulation(mass=1000.0, drag_coeff=50.0, max_throttle=5000.0, dt=0.1)
    
    current_time = 0.0
    duration = 30.0
    
    while current_time <= duration:
        # Profil throttle: przyspieszanie → utrzymanie → hamowanie
        if current_time < 10.0:
            throttle = 80.0  # Przyspieszanie
        elif current_time < 20.0:
            throttle = 40.0  # Utrzymanie prędkości
        else:
            throttle = 10.0  # Hamowanie
            
        state = car.update(throttle)
        car.record_state(current_time, throttle)
        current_time += car.dt
    
    car.plot_results("Test symulacji: Zmienny throttle")
    
    return car


if __name__ == "__main__":
    # Test 1: Stały throttle = 50%
    print("Uruchamianie testów symulacji...\n")
    car1 = test_constant_throttle(throttle_value=50.0, duration=20.0)
    
    # Test 2: Zmienny throttle
    car2 = test_variable_throttle()
    
    print(f"\n{'='*60}")
    print("Testy zakończone pomyślnie!")
    print(f"{'='*60}\n")