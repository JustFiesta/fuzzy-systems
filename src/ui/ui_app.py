"""
Interaktywne UI dla symulatora pojazdu z fuzzy kontrolerem.
Wizualizacja w czasie rzeczywistym ruchu pojazdu po torze owalnym.

Łączy:
- car_simulation.py (model fizyczny pojazdu)
- fuzzy_throttle_controller.py (logika sterowania)
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation

from src.simulation.car_simulation import CarSimulation
from src.core_fuzzy.fuzzy_controller import FuzzyThrottleController


class OvalTrack:
    """Definicja toru owalnego z obliczaniem pozycji i prędkości docelowej."""
    
    def __init__(self, width=100, height=60):
        """
        Args:
            width: szerokość owalu [m]
            height: wysokość owalu [m]
        """
        self.width = width
        self.height = height
        self.a = width / 2  # półoś wielka
        self.b = height / 2  # półoś mała
        
    def get_position(self, distance):
        """
        Oblicza pozycję (x, y) na torze dla danej przebytej odległości.
        
        Args:
            distance: dystans przebytej drogi [m]
        Returns:
            (x, y, angle): pozycja i kąt pojazdu
        """
        # Obwód owalu (przybliżenie Ramanujana)
        h = ((self.a - self.b)**2) / ((self.a + self.b)**2)
        perimeter = np.pi * (self.a + self.b) * (1 + (3*h)/(10 + np.sqrt(4 - 3*h)))
        
        # Normalizacja dystansu do [0, 1]
        t = (distance % perimeter) / perimeter * 2 * np.pi
        
        # Parametryzacja elipsy
        x = self.a * np.cos(t)
        y = self.b * np.sin(t)
        
        # Kąt pojazdu (styczna do toru)
        angle = np.arctan2(-self.a * np.sin(t), self.b * np.cos(t))
        
        return x, y, angle
    
    def get_target_speed(self, distance):
        """
        Zwraca docelową prędkość dla danej pozycji na torze.
        Wyższa prędkość na prostych, niższa w zakrętach.
        
        Args:
            distance: dystans przebytej drogi [m]
        Returns:
            target_speed: docelowa prędkość [m/s]
        """
        x, y, _ = self.get_position(distance)
        
        # Zakręty (boki owalu) - niższa prędkość
        # Proste (góra/dół) - wyższa prędkość
        curve_factor = abs(x) / self.a  # 0 na bokach, 1 na prostych
        
        min_speed = 15.0  # m/s (54 km/h) w zakrętach
        max_speed = 30.0  # m/s (108 km/h) na prostych
        
        return min_speed + (max_speed - min_speed) * curve_factor
    
    def draw(self, ax):
        """Rysuje tor na wykresie."""
        theta = np.linspace(0, 2*np.pi, 200)
        x = self.a * np.cos(theta)
        y = self.b * np.sin(theta)
        
        # Tor zewnętrzny
        ax.plot(x, y, 'k-', linewidth=3, label='Tor')
        
        # Tor wewnętrzny (dla wizualizacji)
        x_inner = (self.a - 5) * np.cos(theta)
        y_inner = (self.b - 5) * np.sin(theta)
        ax.plot(x_inner, y_inner, 'k--', linewidth=1, alpha=0.3)
        
        # Linia środkowa (idealna trajektoria)
        x_mid = (self.a - 2.5) * np.cos(theta)
        y_mid = (self.b - 2.5) * np.sin(theta)
        ax.plot(x_mid, y_mid, 'g--', linewidth=1, alpha=0.5, label='Idealna linia')


class FuzzyCarUI:
    """Główna klasa UI łącząca symulację, kontroler i wizualizację."""
    
    def __init__(self):
        """Inicjalizacja UI i wszystkich komponentów."""
        # Komponenty systemu
        self.car = CarSimulation(mass=1000.0, drag_coeff=50.0, max_throttle=5000.0, dt=0.1)
        self.controller = FuzzyThrottleController()
        self.track = OvalTrack(width=100, height=60)
        
        # Stan symulacji
        self.time = 0.0
        self.running = False
        self.target_speed = 20.0  # m/s
        self.manual_mode = False
        self.manual_throttle = 50.0
        
        # Historia danych
        self.history = {
            'time': [],
            'speed': [],
            'target_speed': [],
            'throttle': [],
            'speed_error': [],
            'position_x': [],
            'position_y': []
        }
        
        # Tworzenie interfejsu
        self._create_ui()
        
    def _create_ui(self):
        """Tworzy layout interfejsu użytkownika."""
        self.fig = plt.figure(figsize=(16, 10))
        self.fig.suptitle('🏎️ Fuzzy Car Controller - Symulacja w czasie rzeczywistym', 
                         fontsize=16, fontweight='bold')
        
        # Layout: 2 rzędy, 3 kolumny
        gs = self.fig.add_gridspec(3, 3, hspace=0.35, wspace=0.3,
                                   left=0.08, right=0.95, top=0.92, bottom=0.08)
        
        # Główny wykres - tor (duży, górny lewy)
        self.ax_track = self.fig.add_subplot(gs[0:2, 0:2])
        self._setup_track_view()
        
        # Wykresy czasu rzeczywistego (prawa kolumna)
        self.ax_speed = self.fig.add_subplot(gs[0, 2])
        self.ax_throttle = self.fig.add_subplot(gs[1, 2])
        
        # Panel sterowania (dolny rząd)
        self.ax_controls = self.fig.add_subplot(gs[2, :])
        self.ax_controls.axis('off')
        
        self._setup_plots()
        self._create_controls()
        
    def _setup_track_view(self):
        """Konfiguruje widok toru."""
        self.ax_track.set_aspect('equal')
        self.ax_track.set_xlim(-60, 60)
        self.ax_track.set_ylim(-40, 40)
        self.ax_track.set_xlabel('X [m]', fontsize=10)
        self.ax_track.set_ylabel('Y [m]', fontsize=10)
        self.ax_track.grid(True, alpha=0.2)
        self.ax_track.set_title('Widok toru', fontweight='bold')
        
        # Rysowanie toru
        self.track.draw(self.ax_track)
        
        # Pojazd (punkt + kierunek)
        self.car_marker, = self.ax_track.plot([], [], 'ro', markersize=15, 
                                              label='Pojazd', zorder=5)
        self.car_direction, = self.ax_track.plot([], [], 'r-', linewidth=3, zorder=5)
        
        # Ślad pojazdu
        self.car_trail, = self.ax_track.plot([], [], 'b-', linewidth=1, 
                                             alpha=0.3, label='Ślad')
        
        self.ax_track.legend(loc='upper right', fontsize=9)
        
        # Tekst z informacjami
        self.info_text = self.ax_track.text(0.02, 0.98, '', transform=self.ax_track.transAxes,
                                           verticalalignment='top', fontsize=9,
                                           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
    def _setup_plots(self):
        """Konfiguruje wykresy z danymi czasowymi."""
        # Prędkość
        self.ax_speed.set_ylabel('Prędkość [m/s]', fontsize=9)
        self.ax_speed.set_title('Prędkość vs Cel', fontsize=10, fontweight='bold')
        self.ax_speed.grid(True, alpha=0.3)
        self.line_speed, = self.ax_speed.plot([], [], 'b-', linewidth=2, label='Rzeczywista')
        self.line_target, = self.ax_speed.plot([], [], 'g--', linewidth=2, label='Docelowa')
        self.ax_speed.legend(fontsize=8, loc='upper right')
        self.ax_speed.set_xlim(0, 20)
        self.ax_speed.set_ylim(0, 35)
        
        # Throttle
        self.ax_throttle.set_xlabel('Czas [s]', fontsize=9)
        self.ax_throttle.set_ylabel('Throttle [%]', fontsize=9)
        self.ax_throttle.set_title('Sterowanie przepustnicą', fontsize=10, fontweight='bold')
        self.ax_throttle.grid(True, alpha=0.3)
        self.line_throttle, = self.ax_throttle.plot([], [], 'r-', linewidth=2)
        self.ax_throttle.set_xlim(0, 20)
        self.ax_throttle.set_ylim(0, 100)
        
    def _create_controls(self):
        """Tworzy panel sterowania z suwakami i przyciskami."""
        # Pozycje kontrolek (w układzie współrzędnych figury)
        control_y = 0.08
        slider_height = 0.02
        slider_width = 0.15
        
        # Suwaki parametrów pojazdu
        ax_mass = plt.axes([0.15, control_y + 0.06, slider_width, slider_height])
        ax_drag = plt.axes([0.15, control_y + 0.03, slider_width, slider_height])
        ax_power = plt.axes([0.15, control_y, slider_width, slider_height])
        
        self.slider_mass = Slider(ax_mass, 'Masa [kg]', 500, 2000, 
                                  valinit=1000, valstep=50)
        self.slider_drag = Slider(ax_drag, 'Opór', 20, 100, 
                                  valinit=50, valstep=5)
        self.slider_power = Slider(ax_power, 'Moc [kN]', 2, 10, 
                                   valinit=5, valstep=0.5)
        
        # Suwak prędkości docelowej
        ax_target = plt.axes([0.45, control_y + 0.03, slider_width, slider_height])
        self.slider_target = Slider(ax_target, 'V cel [m/s]', 10, 35, 
                                    valinit=20, valstep=1)
        
        # Suwak throttle manualnego
        ax_manual_throttle = plt.axes([0.45, control_y, slider_width, slider_height])
        self.slider_manual_throttle = Slider(ax_manual_throttle, 'Manual T [%]', 
                                            0, 100, valinit=50, valstep=1)
        
        # Przyciski
        ax_start = plt.axes([0.70, control_y + 0.04, 0.08, 0.04])
        ax_reset = plt.axes([0.79, control_y + 0.04, 0.08, 0.04])
        ax_mode = plt.axes([0.70, control_y, 0.17, 0.03])
        
        self.btn_start = Button(ax_start, 'Start/Pause', color='lightgreen')
        self.btn_reset = Button(ax_reset, 'Reset', color='lightcoral')
        self.btn_mode = Button(ax_mode, 'Tryb: FUZZY', color='lightyellow')
        
        # Callback'i
        self.slider_mass.on_changed(self._update_car_params)
        self.slider_drag.on_changed(self._update_car_params)
        self.slider_power.on_changed(self._update_car_params)
        self.slider_target.on_changed(self._update_target_speed)
        self.slider_manual_throttle.on_changed(self._update_manual_throttle)
        
        self.btn_start.on_clicked(self._toggle_simulation)
        self.btn_reset.on_clicked(self._reset_simulation)
        self.btn_mode.on_clicked(self._toggle_mode)
        
        # Etykiety
        self.fig.text(0.08, control_y + 0.08, 'PARAMETRY POJAZDU:', 
                     fontsize=10, fontweight='bold')
        self.fig.text(0.38, control_y + 0.08, 'STEROWANIE:', 
                     fontsize=10, fontweight='bold')
        
    def _update_car_params(self, val):
        """Aktualizuje parametry pojazdu."""
        self.car.mass = self.slider_mass.val
        self.car.drag_coeff = self.slider_drag.val
        self.car.max_throttle = self.slider_power.val * 1000
        
    def _update_target_speed(self, val):
        """Aktualizuje prędkość docelową."""
        self.target_speed = self.slider_target.val
        
    def _update_manual_throttle(self, val):
        """Aktualizuje wartość throttle w trybie manualnym."""
        self.manual_throttle = self.slider_manual_throttle.val
        
    def _toggle_simulation(self, event):
        """Uruchamia/zatrzymuje symulację."""
        self.running = not self.running
        
    def _reset_simulation(self, event):
        """Resetuje symulację do stanu początkowego."""
        self.running = False
        self.time = 0.0
        self.car.reset()
        self.history = {key: [] for key in self.history.keys()}
        
        # Czyszczenie wykresów
        self.line_speed.set_data([], [])
        self.line_target.set_data([], [])
        self.line_throttle.set_data([], [])
        self.car_trail.set_data([], [])
        
    def _toggle_mode(self, event):
        """Przełącza między trybem fuzzy a manualnym."""
        self.manual_mode = not self.manual_mode
        if self.manual_mode:
            self.btn_mode.label.set_text('Tryb: MANUAL')
            self.btn_mode.color = 'lightblue'
        else:
            self.btn_mode.label.set_text('Tryb: FUZZY')
            self.btn_mode.color = 'lightyellow'
        
    def update(self, frame):
        """Funkcja aktualizująca animację (wywoływana co klatkę)."""
        if not self.running:
            return
        
        # Aktualna pozycja na torze
        x, y, angle = self.track.get_position(self.car.position)
        
        # Prędkość docelowa na tej pozycji (jeśli używamy adaptacyjnej)
        # target_speed = self.track.get_target_speed(self.car.position)
        target_speed = self.target_speed  # lub stała wartość
        
        # Obliczenie błędu prędkości (w km/h dla kontrolera)
        speed_error = (target_speed - self.car.speed) * 3.6
        
        # Obliczenie throttle
        if self.manual_mode:
            throttle = self.manual_throttle
        else:
            throttle = self.controller.compute_throttle(speed_error, self.car.acceleration)
        
        # Aktualizacja stanu pojazdu
        self.car.update(throttle)
        self.time += self.car.dt
        
        # Zapisanie historii
        self.history['time'].append(self.time)
        self.history['speed'].append(self.car.speed)
        self.history['target_speed'].append(target_speed)
        self.history['throttle'].append(throttle)
        self.history['speed_error'].append(speed_error)
        self.history['position_x'].append(x)
        self.history['position_y'].append(y)
        
        # Aktualizacja wizualizacji pojazdu
        self.car_marker.set_data([x], [y])
        
        # Kierunek pojazdu (strzałka)
        arrow_length = 5
        dx = arrow_length * np.cos(angle)
        dy = arrow_length * np.sin(angle)
        self.car_direction.set_data([x, x + dx], [y, y + dy])
        
        # Ślad pojazdu (ostatnie 50 punktów)
        trail_length = min(50, len(self.history['position_x']))
        self.car_trail.set_data(
            self.history['position_x'][-trail_length:],
            self.history['position_y'][-trail_length:]
        )
        
        # Tekst z informacjami
        info = (f"⏱️ Czas: {self.time:.1f} s\n"
                f"📍 Pozycja: {self.car.position:.1f} m\n"
                f"🏁 Prędkość: {self.car.speed:.1f} m/s ({self.car.speed*3.6:.1f} km/h)\n"
                f"🎯 Cel: {target_speed:.1f} m/s ({target_speed*3.6:.1f} km/h)\n"
                f"⚡ Throttle: {throttle:.1f} %\n"
                f"📊 Błąd: {speed_error:.1f} km/h")
        self.info_text.set_text(info)
        
        # Aktualizacja wykresów czasowych
        if len(self.history['time']) > 0:
            # Okno czasowe (ostatnie 20 sekund)
            time_window = 20
            if self.time > time_window:
                self.ax_speed.set_xlim(self.time - time_window, self.time)
                self.ax_throttle.set_xlim(self.time - time_window, self.time)
            
            self.line_speed.set_data(self.history['time'], self.history['speed'])
            self.line_target.set_data(self.history['time'], self.history['target_speed'])
            self.line_throttle.set_data(self.history['time'], self.history['throttle'])
        
        return (self.car_marker, self.car_direction, self.car_trail, 
                self.line_speed, self.line_target, self.line_throttle, self.info_text)
    
    def run(self):
        """Uruchamia interfejs użytkownika."""
        # Animacja z ~30 FPS (interwał 33ms)
        self.anim = animation.FuncAnimation(
            self.fig, self.update, interval=33, blit=False, cache_frame_data=False
        )
        
        plt.show()


# ============================================================================
# URUCHOMIENIE APLIKACJI
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print(" 🏎️  FUZZY CAR CONTROLLER - INTERAKTYWNA SYMULACJA")
    print("=" * 70)
    print()
    print("Uruchamianie interfejsu użytkownika...")
    print()
    print("INSTRUKCJA:")
    print("  1. Naciśnij 'Start/Pause' aby rozpocząć symulację")
    print("  2. Używaj suwaków do zmiany parametrów pojazdu w czasie rzeczywistym")
    print("  3. Przełączaj między trybem FUZZY (automatyczny) a MANUAL")
    print("  4. Obserwuj, jak pojazd jedzie po torze owalnym")
    print()
    print("=" * 70)
    print()
    
    app = FuzzyCarUI()
    app.run()
