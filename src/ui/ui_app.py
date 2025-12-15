"""
Zoptymalizowane UI dla symulatora pojazdu z fuzzy kontrolerem.
Używa PyQtGraph dla wysokiej wydajności renderowania w czasie rzeczywistym.

Łączy:
- car_simulation.py (model fizyczny pojazdu)
- fuzzy_controller.py (logika sterowania)
"""

import sys
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
import pyqtgraph as pg

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
        self.a = width / 2
        self.b = height / 2
        
        # Pre-kalkulacja punktów toru dla wydajności
        self._cache_track_points()
        
    def _cache_track_points(self):
        """Pre-kalkuluje punkty toru dla szybszego rysowania."""
        theta = np.linspace(0, 2*np.pi, 200)
        self.track_x = self.a * np.cos(theta)
        self.track_y = self.b * np.sin(theta)
        
        # Tor wewnętrzny
        self.inner_x = (self.a - 5) * np.cos(theta)
        self.inner_y = (self.b - 5) * np.sin(theta)
        
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


class FuzzyCarUI(QtWidgets.QMainWindow):
    """Główna klasa UI z PyQtGraph - wysoka wydajność renderowania."""
    
    def __init__(self):
        """Inicjalizacja UI i wszystkich komponentów."""
        super().__init__()
        
        # Komponenty systemu
        self.car = CarSimulation(mass=1000.0, drag_coeff=50.0, max_throttle=5000.0, dt=0.1)
        self.controller = FuzzyThrottleController()
        self.track = OvalTrack(width=100, height=60)
        
        # Stan symulacji
        self.time = 0.0
        self.running = False
        self.target_speed = 20.0
        self.manual_mode = False
        self.manual_throttle = 50.0
        
        # Konfiguracja wydajności - aktualizacja wizualizacji co N kroków symulacji
        self.sim_step_counter = 0
        self.viz_update_interval = 1  # Aktualizuj wizualizację co 1 krok (można zwiększyć do 2-3)
        
        # Historia danych (ograniczona długość dla wydajności)
        self.max_history_length = 200  # ~20s przy 10 FPS wizualizacji
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
        self._init_ui()
        
        # Timer symulacji (33ms = ~30 FPS)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self._simulation_step)
        self.timer.setInterval(33)
        
    def _init_ui(self):
        """Inicjalizacja interfejsu użytkownika."""
        self.setWindowTitle('🏎️ Fuzzy Car Controller - Zoptymalizowana Symulacja')
        self.setGeometry(100, 100, 1400, 800)
        
        # Widget centralny
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout główny
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        
        # Layout wykresów (górna część)
        plots_layout = QtWidgets.QHBoxLayout()
        
        # Lewa strona - tor
        self.track_widget = pg.GraphicsLayoutWidget()
        self.track_plot = self.track_widget.addPlot(title="Widok toru")
        self._setup_track_plot()
        plots_layout.addWidget(self.track_widget, stretch=2)
        
        # Prawa strona - wykresy czasowe
        right_plots = pg.GraphicsLayoutWidget()
        self.speed_plot = right_plots.addPlot(row=0, col=0, title="Prędkość vs Cel")
        self.throttle_plot = right_plots.addPlot(row=1, col=0, title="Sterowanie przepustnicą")
        self._setup_time_plots()
        plots_layout.addWidget(right_plots, stretch=1)
        
        main_layout.addLayout(plots_layout, stretch=3)
        
        # Panel sterowania (dolna część)
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel, stretch=1)
        
        # Panel informacji (górny pasek)
        self.info_label = QtWidgets.QLabel()
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 10px;
                border: 2px solid #333;
                border-radius: 5px;
                font-size: 11pt;
                font-weight: bold;
            }
        """)
        self._update_info_label()
        main_layout.insertWidget(0, self.info_label)
        
    def _setup_track_plot(self):
        """Konfiguruje wykres toru."""
        self.track_plot.setAspectLocked(True)
        self.track_plot.setXRange(-60, 60)
        self.track_plot.setYRange(-40, 40)
        self.track_plot.setLabel('bottom', 'X [m]')
        self.track_plot.setLabel('left', 'Y [m]')
        self.track_plot.showGrid(x=True, y=True, alpha=0.3)
        
        # Rysowanie toru (statyczne, nie będzie aktualizowane)
        self.track_plot.plot(self.track.track_x, self.track.track_y, 
                            pen=pg.mkPen('k', width=3), name='Tor')
        self.track_plot.plot(self.track.inner_x, self.track.inner_y, 
                            pen=pg.mkPen('k', width=1, style=QtCore.Qt.DashLine))
        
        # Pojazd (dynamiczny)
        self.car_marker = pg.ScatterPlotItem(size=15, pen=pg.mkPen(None), 
                                            brush=pg.mkBrush('r'))
        self.track_plot.addItem(self.car_marker)
        
        # Kierunek pojazdu (strzałka)
        self.car_arrow = pg.PlotDataItem(pen=pg.mkPen('r', width=3))
        self.track_plot.addItem(self.car_arrow)
        
        # Ślad pojazdu
        self.car_trail = pg.PlotDataItem(pen=pg.mkPen('b', width=2, style=QtCore.Qt.DotLine))
        self.track_plot.addItem(self.car_trail)
        
    def _setup_time_plots(self):
        """Konfiguruje wykresy czasowe."""
        # Prędkość
        self.speed_plot.setLabel('left', 'Prędkość [m/s]')
        self.speed_plot.setLabel('bottom', 'Czas [s]')
        self.speed_plot.showGrid(x=True, y=True, alpha=0.3)
        self.speed_plot.setYRange(0, 35)
        
        self.speed_curve = self.speed_plot.plot(pen=pg.mkPen('b', width=2), name='Rzeczywista')
        self.target_curve = self.speed_plot.plot(pen=pg.mkPen('g', width=2, style=QtCore.Qt.DashLine), 
                                                 name='Docelowa')
        
        # Throttle
        self.throttle_plot.setLabel('left', 'Throttle [%]')
        self.throttle_plot.setLabel('bottom', 'Czas [s]')
        self.throttle_plot.showGrid(x=True, y=True, alpha=0.3)
        self.throttle_plot.setYRange(0, 100)
        
        self.throttle_curve = self.throttle_plot.plot(pen=pg.mkPen('r', width=2))
        
    def _create_control_panel(self):
        """Tworzy panel sterowania z suwakami i przyciskami."""
        panel = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(panel)
        
        # Sekcja 1: Parametry pojazdu
        params_group = QtWidgets.QGroupBox("Parametry pojazdu")
        params_layout = QtWidgets.QFormLayout()
        
        # Zmiana: Przechowujemy zarówno kontenery jak i suwaki
        self.mass_container, self.mass_slider = self._create_slider(500, 2000, 1000, 50)
        self.drag_container, self.drag_slider = self._create_slider(20, 100, 50, 5)
        self.power_container, self.power_slider = self._create_slider(2, 10, 5, 0.5, scale=1000)
        
        params_layout.addRow("Masa [kg]:", self.mass_container)
        params_layout.addRow("Opór:", self.drag_container)
        params_layout.addRow("Moc [kN]:", self.power_container)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Sekcja 2: Sterowanie
        control_group = QtWidgets.QGroupBox("Sterowanie")
        control_layout = QtWidgets.QFormLayout()
        
        self.target_container, self.target_slider = self._create_slider(10, 35, 20, 1)
        self.manual_throttle_container, self.manual_throttle_slider = self._create_slider(0, 100, 50, 1)
        
        control_layout.addRow("Prędkość docelowa [m/s]:", self.target_container)
        control_layout.addRow("Manual Throttle [%]:", self.manual_throttle_container)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Sekcja 3: Przyciski
        buttons_layout = QtWidgets.QHBoxLayout()
        
        self.start_btn = QtWidgets.QPushButton("▶ Start")
        self.start_btn.setStyleSheet("QPushButton { background-color: #90EE90; font-weight: bold; padding: 10px; }")
        self.start_btn.clicked.connect(self._toggle_simulation)
        
        self.reset_btn = QtWidgets.QPushButton("🔄 Reset")
        self.reset_btn.setStyleSheet("QPushButton { background-color: #FFB6C1; font-weight: bold; padding: 10px; }")
        self.reset_btn.clicked.connect(self._reset_simulation)
        
        self.mode_btn = QtWidgets.QPushButton("🤖 Tryb: FUZZY")
        self.mode_btn.setStyleSheet("QPushButton { background-color: #FFFFE0; font-weight: bold; padding: 10px; }")
        self.mode_btn.clicked.connect(self._toggle_mode)
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addWidget(self.mode_btn)
        
        layout.addLayout(buttons_layout)
        
        # Callback'i suwaków - teraz używamy właściwych suwaków
        self.mass_slider.valueChanged.connect(self._update_car_params)
        self.drag_slider.valueChanged.connect(self._update_car_params)
        self.power_slider.valueChanged.connect(self._update_car_params)
        self.target_slider.valueChanged.connect(self._update_target_speed)
        self.manual_throttle_slider.valueChanged.connect(self._update_manual_throttle)
        
        return panel
        
    def _create_slider(self, min_val, max_val, default, step, scale=1):
        """Helper do tworzenia suwaków z labelką wartości."""
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(int(min_val / step))
        slider.setMaximum(int(max_val / step))
        slider.setValue(int(default / step))
        slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        slider.setTickInterval(int((max_val - min_val) / step / 10))
        
        label = QtWidgets.QLabel(f"{default:.1f}")
        label.setMinimumWidth(50)
        label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        # Zmiana: przechowujemy step i scale w sliderze
        slider._step = step
        slider._scale = scale
        
        def update_label(value):
            label.setText(f"{value * step * scale:.1f}")
            
        slider.valueChanged.connect(update_label)
        
        layout.addWidget(slider)
        layout.addWidget(label)
        
        return container, slider  # Zmiana: zwracamy zarówno kontener jak i suwak
    
    def _update_car_params(self):
        """Aktualizuje parametry pojazdu."""
        self.car.mass = self.mass_slider.value() * self.mass_slider._step * self.mass_slider._scale
        self.car.drag_coeff = self.drag_slider.value() * self.drag_slider._step * self.drag_slider._scale
        self.car.max_throttle = self.power_slider.value() * self.power_slider._step * self.power_slider._scale
        
    def _update_target_speed(self):
        """Aktualizuje prędkość docelową."""
        self.target_speed = self.target_slider.value() * self.target_slider._step * self.target_slider._scale
        
    def _update_manual_throttle(self):
        """Aktualizuje manualny throttle."""
        self.manual_throttle = self.manual_throttle_slider.value() * self.manual_throttle_slider._step * self.manual_throttle_slider._scale
        
    def _toggle_simulation(self):
        """Uruchamia/zatrzymuje symulację."""
        self.running = not self.running
        if self.running:
            self.start_btn.setText("⏸ Pause")
            self.timer.start()
        else:
            self.start_btn.setText("▶ Start")
            self.timer.stop()
            
    def _reset_simulation(self):
        """Resetuje symulację do stanu początkowego."""
        self.running = False
        self.timer.stop()
        self.start_btn.setText("▶ Start")
        
        self.time = 0.0
        self.sim_step_counter = 0
        self.car.reset()
        
        # Czyszczenie historii
        for key in self.history:
            self.history[key].clear()
        
        # Czyszczenie wykresów
        self.speed_curve.setData([], [])
        self.target_curve.setData([], [])
        self.throttle_curve.setData([], [])
        self.car_trail.setData([], [])
        
        self._update_info_label()
        
    def _toggle_mode(self):
        """Przełącza między trybem fuzzy a manualnym."""
        self.manual_mode = not self.manual_mode
        if self.manual_mode:
            self.mode_btn.setText("👤 Tryb: MANUAL")
            self.mode_btn.setStyleSheet("QPushButton { background-color: #ADD8E6; font-weight: bold; padding: 10px; }")
        else:
            self.mode_btn.setText("🤖 Tryb: FUZZY")
            self.mode_btn.setStyleSheet("QPushButton { background-color: #FFFFE0; font-weight: bold; padding: 10px; }")
    
    def _simulation_step(self):
        """Główna pętla symulacji - wywoływana przez timer."""
        if not self.running:
            return
        
        # Aktualna pozycja na torze
        x, y, angle = self.track.get_position(self.car.position)
        
        # Prędkość docelowa
        target_speed = self.target_speed
        
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
        self._append_history(x, y, target_speed, throttle, speed_error)
        
        # Aktualizacja wizualizacji (z redukcją częstotliwości)
        self.sim_step_counter += 1
        if self.sim_step_counter >= self.viz_update_interval:
            self._update_visualization(x, y, angle)
            self.sim_step_counter = 0
    
    def _append_history(self, x, y, target_speed, throttle, speed_error):
        """Dodaje dane do historii z ograniczeniem długości."""
        self.history['time'].append(self.time)
        self.history['speed'].append(self.car.speed)
        self.history['target_speed'].append(target_speed)
        self.history['throttle'].append(throttle)
        self.history['speed_error'].append(speed_error)
        self.history['position_x'].append(x)
        self.history['position_y'].append(y)
        
        # Ograniczenie długości historii
        if len(self.history['time']) > self.max_history_length:
            for key in self.history:
                self.history[key].pop(0)
    
    def _update_visualization(self, x, y, angle):
        """Aktualizuje wszystkie elementy wizualizacji."""
        # Pozycja pojazdu
        self.car_marker.setData([x], [y])
        
        # Kierunek pojazdu (strzałka)
        arrow_length = 5
        dx = arrow_length * np.cos(angle)
        dy = arrow_length * np.sin(angle)
        self.car_arrow.setData([x, x + dx], [y, y + dy])
        
        # Ślad pojazdu (ostatnie 50 punktów)
        trail_length = min(50, len(self.history['position_x']))
        if trail_length > 0:
            self.car_trail.setData(
                self.history['position_x'][-trail_length:],
                self.history['position_y'][-trail_length:]
            )
        
        # Aktualizacja wykresów czasowych
        if len(self.history['time']) > 1:
            # Downsampling dla wydajności - pokazuj co N-ty punkt
            downsample = max(1, len(self.history['time']) // 100)
            
            time_data = self.history['time'][::downsample]
            speed_data = self.history['speed'][::downsample]
            target_data = self.history['target_speed'][::downsample]
            throttle_data = self.history['throttle'][::downsample]
            
            self.speed_curve.setData(time_data, speed_data)
            self.target_curve.setData(time_data, target_data)
            self.throttle_curve.setData(time_data, throttle_data)
            
            # Automatyczne dopasowanie zakresu X (okno czasowe 20s)
            time_window = 20
            if self.time > time_window:
                self.speed_plot.setXRange(self.time - time_window, self.time)
                self.throttle_plot.setXRange(self.time - time_window, self.time)
        
        # Aktualizacja informacji
        self._update_info_label()
    
    def _update_info_label(self):
        """Aktualizuje pasek informacyjny."""
        info_text = (
            f"⏱️ Czas: {self.time:.1f}s  |  "
            f"📍 Przebyty dystnans: {self.car.position:.1f}m  |  "
            f"🏁 Prędkość: {self.car.speed:.1f} m/s ({self.car.speed*3.6:.1f} km/h)  |  "
            f"🎯 Prędkość docelowa: {self.target_speed:.1f} m/s ({self.target_speed*3.6:.1f} km/h)  |  "
            f"⚡ Przepustnica: {self.history['throttle'][-1] if self.history['throttle'] else 0:.1f}%  |  "
            f"📊 Błąd: {self.history['speed_error'][-1] if self.history['speed_error'] else 0:.1f} km/h"
        )
        self.info_label.setText(info_text)


def main():
    """Uruchomienie aplikacji."""
    print("=" * 70)
    print("FUZZY CAR CONTROLLER")
    print("=" * 70)
    print()
    
    app = QtWidgets.QApplication(sys.argv)
    
    # Styl aplikacji
    app.setStyle('Fusion')
    
    # Główne okno
    window = FuzzyCarUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
