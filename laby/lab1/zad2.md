# Działanie tipper.py

* Bierze ocenę obsługi (0-10) i na tej podstawie decyduje o wysokości napiwku (0-20%)

* Są 3 kategorie obsługi: BAD, MEDIUM, HIGH - zdefiniowane jako zbiory rozmyte

* Są 3 kategorie napiwku: POOR, AVERAGE, GENEROUS - też zbiory rozmyte

* Reguły są proste: zła obsługa → mały napiwek, średnia → średni, dobra → duży

* Działa tak: bierze ostrą liczbę, zamienia na rozmyte wartości przynależności do każdej kategorii, aplikuje reguły, i z powrotem zamienia rozmyty wynik na ostrą liczbę (napiwek)
