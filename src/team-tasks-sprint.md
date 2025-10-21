# Struktura zespołu

Osoba	Moduł	Główna odpowiedzialność	Kluczowe technologie
Inżynier 1 – FuzzyCore Developer	core_fuzzy/	logika rozmyta: definicja zmiennych, funkcji przynależności, reguł, defuzyfikacja	scikit-fuzzy, numpy, matplotlib
Inżynier 2 – Simulation Engineer	simulation/	model fizyczny pojazdu, pętla symulacyjna, integracja z fuzzy outputem	numpy, time, opcjonalnie asyncio
Inżynier 3 – UI Engineer	ui/	interfejs użytkownika, tor 2D, grafika pojazdu, suwaki, integracja z symulacją	streamlit lub pygame

---

## Prompt 1 – FuzzyCore Developer

### Rola:
Jesteś doświadczonym inżynierem systemów rozmytych, który ma zaprojektować i zaimplementować moduł logiki rozmytej sterującej mocą silnika samochodu w symulatorze toru jazdy.

### Cel:
Stwórz samodzielny moduł fuzzy_controller.py odpowiedzialny za:

definicję zmiennych lingwistycznych (speed_error, acceleration, throttle)

dobór funkcji przynależności (trójkątne/trapezowe)

zestaw reguł IF–THEN (9–12 reguł)

wnioskowanie i defuzyfikację (centroid)

interfejs: compute_throttle(speed_error, acceleration) -> float

Wymagania techniczne:

Biblioteki: numpy, skfuzzy

KISS: każda funkcja ma jedną odpowiedzialność

Zwracaj dane w formacie numerycznym (float) z zakresu [0, 100]

Dodaj wizualizację zbiorów rozmytych i reguł w formie funkcji plot_memberships()

Założenia wejść/wyjść:

speed_error: zakres [-30, 30]

acceleration: zakres [-10, 10]

throttle: zakres [0, 100]

Na końcu modułu:
pokaż przykład użycia (symulacja kilku wartości i wykres throttle vs error).

---

## Prompt 2 – Simulation Engineer

Rola:
Jesteś inżynierem systemów dynamicznych. Twoim zadaniem jest zbudować moduł symulacji fizyki pojazdu dla fuzzy kontrolera.

Cel:
Stwórz moduł car_simulation.py, który modeluje ruch pojazdu po torze (1D lub 2D).

Założenia:

Symulacja czasu dyskretnego (Δt = 0.1 s)

Parametry pojazdu: masa, opór, siła napędowa

Stan: pozycja, prędkość, przyspieszenie

Aktualizacja w pętli:
acceleration = (throttle - drag_coeff * speed) / mass
speed += acceleration * Δt
position += speed * Δt

Interfejs:

update(throttle: float, dt: float) -> dict zwraca słownik ze stanem (speed, acceleration, position)

reset() – resetuje stan

Integracja:

Ma być niezależny od logiki fuzzy (throttle to po prostu wejście liczbowe)

Przygotuj test symulacji: zadane throttle = 50 → pokaż wykres prędkości w czasie.

Biblioteki: numpy, matplotlib, time

---

## Prompt 3 – UI Engineer

### Rola:
Jesteś inżynierem frontendowym tworzącym interaktywny interfejs symulatora jazdy pojazdu sterowanego logiką rozmytą.

### Cel:
Stwórz moduł ui_app.py (preferowany streamlit, alternatywnie pygame), który:

Wyświetla tor 2D (np. elipsa lub pętla)

Pokazuje samochód (punkt/grafika) poruszający się po torze

Udostępnia suwaki:

prędkość docelowa (target_speed)

włącz/wyłącz fuzzy control

Wyświetla w czasie rzeczywistym:

prędkość, throttle, różnicę prędkości

Opcjonalnie: drugi samochód z innym kontrolerem

Integracja:

Importuj moduły:

from core_fuzzy.fuzzy_controller import compute_throttle  
from simulation.car_simulation import Car


W pętli (lub callbacku) aktualizuj stan i wizualizuj.

Zadbaj o modularność i czytelny kod.

Funkcjonalność testowa:
Tryb demo – auto jedzie po torze, fuzzy utrzymuje prędkość ±2 km/h.
