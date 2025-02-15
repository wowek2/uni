import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


'''PARAMETRY'''
g = 9.81            # przyspieszenie grawitacyjne
x_start = -5.0      # początek dziedziny
x_end =  10.0       # koniec dziedziny
Nx = 500            # liczba punktów siatki
T_max = 10.0        # maksymalny czas symulacji
CFL = 0.5           # stała w warunku CFL

'''SIATKA PRZESTRZENNA'''
x = np.linspace(x_start, x_end, Nx)
dx = x[1] - x[0]

'''RZEŹBA DNA'''
z_b = 1/(1+np.exp(2.71**((x-4)*6))) + 1 # sigmoid (lekko podrasowany)

'''WARUNKI POCZĄTKOWE'''
# Po lewej woda wyżej, po prawej niżedj
h_left = 1
h_right = 0.3

h = np.where(x < 4.0, h_left, h_right)  # Przyporządkowuje poziom wody w zależności, po której stronie tamy jesteśmy (tama jest dla x=4, patrz rzeźba terenu)
q = np.zeros_like(x)                    # Na początku woda w spoczynku (nawet ta za tamą)


'''FUNKCJA STRUMIENIA'''
# Wzór: F(U) = (q, (q^2 / h) + 0.5*g*h^2)
def flux(h, q):
    F1 = q
    F2 = (q**2 / h) + 0.5*g*(h**2)
    return F1, F2

'''WYKRESIK'''
fig, ax = plt.subplots()

line_water, = ax.plot([], [], 'b-', label='Lustro wody')
line_bottom, = ax.plot(x, z_b, 'k--', label='Dno')

ax.set_xlim(x_start, x_end)
# Ustawiamy maksymalny zakres wysokości, aby zmieścić początkowy poziom wody
max_level = np.max(z_b + h)
ax.set_ylim(0, 1.2 * max_level)

ax.set_xlabel('x')
ax.set_ylabel('wysokość (m)')
ax.set_title('1D płytka woda, przerwanie tamy')
ax.legend()

time_text = ax.text(0.02, 0.9, '', transform=ax.transAxes)

def init():
    line_water.set_data([], [])
    time_text.set_text('')
    return line_water, time_text

def update(frame):
    global h, q
    
    # Liczenie kroku czasowego (CFL)
    u = np.where(h > 1e-8, q/h, 0.0)
    c = np.sqrt(g*h)
    max_speed = np.max(np.abs(u) + c)
    dt = CFL * dx / max_speed if max_speed > 1e-10 else 1e-6
    
    # zatrzymanie symulacji
    if frame*dt > T_max:
        anim.event_source.stop()
        return line_water, time_text
    
    # Liczenie wektorów strumienia F1, F2 dla każdego punktu naszej siatki
    F1, F2 = flux(h, q)
    
    # Kopiujemy areye dla n+1 (kolejna iteracja)
    h_new = np.copy(h)
    q_new = np.copy(q)
    
    # Pochodna dna:
    zL = np.roll(z_b, 1)            # Przesuwamy wektor o jedno miejsce w prawo
    zR = np.roll(z_b, -1)           # Przesuwamy wektor o jedno miejsce w lewo
    dzb_dx = (zR - zL) / (2*dx)     # Liczymy różnice wysokości pomiędzyy tymi przesunięciami
    
    # Schemat Lax-Friedrichsa
    for i in range(1, Nx-1):
        # h
        h_new[i] = 0.5*(h[i+1] + h[i-1]) - 0.5*(dt/dx)*(F1[i+1] - F1[i-1])
        
        # q
        q_new[i] = 0.5*(q[i+1] + q[i-1]) - 0.5*(dt/dx)*(F2[i+1] - F2[i-1])
        
        # rzeźba dna
        q_new[i] -= dt * g * h[i] * dzb_dx[i]
    

    # Zachowanie na końcach dziedziny
    # Zasadniczo to po prostu kopiujemy wartości sąsiadów
    h_new[0] = h_new[1]
    q_new[0] = q_new[1]
    h_new[-1] = h_new[-2]
    q_new[-1] = q_new[-2]
    
    # Aktualizujemy stan
    h = h_new
    q = q_new
    
    # Nowe dane do wykresu + update czasu
    line_water.set_data(x, z_b + h)  # lustro = dno + głębokość
    time_text.set_text(f't = {frame*dt:.3f} s')
    
    return line_water, time_text

"""ANIMOWANIE WYKRESU"""
anim = FuncAnimation(fig, update, frames=10_000, interval=1,
                     init_func=init, blit=True)

plt.show()