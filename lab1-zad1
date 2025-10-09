import numpy as np
import matplotlib.pyplot as plt

# zad1 - funkcja trojkatna
def triangle(x, a, b, c):
    """
    fun przyn trojkatna
    a - lewy dolny wierzchołek
    b - gorny wierzchołek  
    c - pr dolny wierzchołek
    """
    # czy x jest poniżej a lub powyżej c - wtedy przynależność = 0
    if x <= a or x >= c:
        return 0.0
    # x jest między a i b - rośnie liniowo od 0 do 1
    elif a < x <= b:
        return (x - a) / (b - a)
    # x jest między b i c - maleje liniowo od 1 do 0
    elif b < x < c:
        return (c - x) / (c - b)
    else:
        return 0.0

# zad1 - funkcja trapezowa
def trapezoid(x, a, b, c, d):
    """
    fun przyn trapezowa
    a - l dolny wierzchołek
    b - l górny wierzchołek
    c - p górny wierzchołek  
    d - p dolny wierzchołek
    """
    # na lewo lub prawo od trapezu
    if x <= a or x >= d:
        return 0.0
    # na plaskim szczycie trapezu
    elif b <= x <= c:
        return 1.0
    # na lewym zboczu (rosnie)
    elif a < x < b:
        return (x - a) / (b - a)
    # na prawym zboczu (maleje)
    elif c < x < d:
        return (d - x) / (d - c)
    else:
        return 0.0

# test funkcji -  wart brzegowe
print("=== TEST FUNKCJI TROJKATNEJ ===")
x_values = [2, 3, 4, 5, 6]
for x in x_values:
    result = triangle(x, 3, 5, 7)  # trojkat od 3 do 7 z wierzchołkiem w 5
    print(f"x={x}: {result}")

print("\n=== TEST FUNKCJI TRAPEZOWEJ ===")  
for x in x_values:
    result = trapezoid(x, 2, 4, 6, 8)  # trapez od 2 do 8 z wyplaszczeniem od 4 do 6
    print(f"x={x}: {result}")

# wizualizacje
x_range = np.linspace(0, 10, 100)
triangle_vals = [triangle(x, 3, 5, 7) for x in x_range]
trapezoid_vals = [trapezoid(x, 2, 4, 6, 8) for x in x_range]

plt.figure(figsize=(12, 4))

plt.subplot(1, 2, 1)
plt.plot(x_range, triangle_vals, 'b-', linewidth=2)
plt.title('Funkcja trójkątna')
plt.grid(True)

plt.subplot(1, 2, 2) 
plt.plot(x_range, trapezoid_vals, 'r-', linewidth=2)
plt.title('Funkcja trapezowa')
plt.grid(True)

plt.tight_layout()
plt.show()
