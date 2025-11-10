# Cel projektu

Stworzyć symulację jazdy pojazdu po torze, w której logika rozmyta steruje jego prędkością, aby utrzymać zadaną wartość (cruise control).
UI pokazuje tor, pozycję auta, aktualną prędkość i moc silnika.
W przyszłości łatwo dodać drugi samochód i logikę „ścigania”.

## Zakres systemu rozmytego (pierwszy etap)
Typ zmiennej	Nazwa	Opis	Jednostka	Zakres
Wejście 1	speed_error	różnica między prędkością zadaną a aktualną	km/h	[-30, +30]
Wejście 2	acceleration	tempo zmian prędkości (czy auto już przyspiesza/zwalnia)	km/h/s	[-10, +10]
Wyjście	throttle	sygnał sterujący mocą silnika (lub pedałem gazu)	%	[0, 100]

## Koncepcja lingwistyczna

### Zmienna speed_error może przyjmować wartości lingwistyczne:

NB (Negative Big) – za bardzo przekracza prędkość

NS (Negative Small) – nieco za szybki

Z (Zero) – jedzie prawidłowo

PS (Positive Small) – lekko za wolny

PB (Positive Big) – bardzo za wolny

### Zmienna acceleration:

N – hamuje

Z – bez zmian

P – przyspiesza

### Zmienna wyjściowa throttle:

Low, Medium, High

## Baza reguł (przykład naturalny)

- IF speed_error is PB AND acceleration is N THEN throttle is High
- IF speed_error is Z AND acceleration is Z THEN throttle is Medium
- IF speed_error is NB AND acceleration is P THEN throttle is Low

(W praktyce opracujemy ok. 9 reguł, żeby pokryć wszystkie kombinacje.)

## Dane i źródła

Dla realistycznych danych (symulacja ruchu, prędkości, przyspieszenia, torów) możemy skorzystać z open datasets, np.:

- Udacity Self-Driving Car Dataset
- CARLA simulator datasets
- NGSIM US-101 or I-80 traffic datasets

Na początek jednak zasymulujemy dane w Pythonie (numpy), by testować fuzzy logic niezależnie od UI.

## Plan techniczny implementacji

Core fuzzy logic – scikit-fuzzy do wnioskowania:

- definiujemy zbiory rozmyte
- ustalamy reguły
- wnioskowanie + defuzyfikacja
- Simulation loop – prosty model fizyczny pojazdu (prędkość ← moc – opory)
- UI / wizualizacja – streamlit albo pygame:
- tor 2D
- samochód jako grafika
- suwaki: prędkość docelowa, warunki, włącz/wyłącz fuzzy logic
- (Opcjonalnie) drugi samochód → osobny kontroler fuzzy + wspólna symulacja.
- spełnienie zasad modularności, KISS, jednej odpowiedzialności funkcji/klasy
