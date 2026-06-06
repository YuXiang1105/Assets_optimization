import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import random
import math

m1 = 0.1180850933
m2 = 0.1619481497
m3 = 0.0771816605
v1 = 0.03492332644
v2 = 0.02776645397
v3 = 0.03505910984
cv12 = 0.001666029016
cv13 = 0.0005078163229
cv23 = 0.0005112105901

# Gröbner se calcula UNA sola vez
p1, p2, E, V = sp.symbols('p1 p2 E V', real=True)
p3 = 1 - p1 - p2
pol2 = E - (m1*p1 + m2*p2 + m3*p3)
pol3 = V - (v1*p1**2 + v2*p2**2 + v3*p3**2 +
            2*cv12*p1*p2 + 2*cv13*p1*p3 + 2*cv23*p2*p3)

G = sp.groebner([pol2, pol3], p1, p2, E, V, order='lex')
eq1, eq2 = G[0], G[1]

p1_expr = sp.solve(eq1, p1)[0]
eq2_sub = sp.simplify(eq2.subs(p1, p1_expr))
sol_p2 = sp.solve(eq2_sub, p2)
p1_sol = sol_p2[0]
p2_sol = sol_p2[1]

# Ahora el bucle solo sustituye E y evalúa
MenoresVarianzas = []
Esperanzas = []
recorrer = np.linspace(0.005, 0.05, 500)

#El E_valor solo puede estar entre la rentabilidad minima y maxima
recorrer = np.linspace(0.01, 0.06, 1000)
E_valor = 0.08
while E_valor <= 0.16:
    p1_E = p1_sol.subs(E, E_valor)
    p2_E = p2_sol.subs(E, E_valor)
    f_p1 = sp.lambdify(V, p1_E, "numpy")
    f_p2 = sp.lambdify(V, p2_E, "numpy")

    V_frontera, p1_f, p2_f, p3_f = [], [], [], []

    for V_valor in recorrer:
        try:
            pol1It = float(np.real(f_p1(V_valor)))
            pol2It = float(np.real(f_p2(V_valor)))
            pol3It = 1 - pol1It - pol2It
            if (np.isfinite(pol1It) and np.isfinite(pol2It) and np.isfinite(pol3It)
                    and pol1It >= 0 and pol2It >= 0 and pol3It >= 0):
                V_frontera.append(V_valor)
                p1_f.append(pol1It)
                p2_f.append(pol2It)
                p3_f.append(pol3It)
        except:
            continue

    if V_frontera:
        i = np.argmin(V_frontera)
        MenoresVarianzas.append([E_valor, V_frontera[i], p1_f[i], p2_f[i], p3_f[i]])
        Esperanzas.append(E_valor)
    E_valor += 0.002


frontera = list(zip(Esperanzas, MenoresVarianzas))
print(frontera)

E_vals = []
V_vals = []

for row in MenoresVarianzas:
    E_vals.append(row[0])
    V_vals.append(row[1])

E_vals = np.array(E_vals)
V_vals = np.array(V_vals)

# ordenar por E 
idx = np.argsort(E_vals)
E_vals = E_vals[idx]
V_vals = V_vals[idx]

plt.figure()
plt.plot(E_vals, V_vals)

plt.xlabel("Retorno esperado (E)")
plt.ylabel("Varianza (V)")
plt.title("Frontera eficiente")

plt.xlim(0, 0.15)
plt.ylim(0, 0.05)

plt.grid(True)

plt.savefig("frontera_eficiente.png", dpi=300, bbox_inches="tight")
plt.show()

#Hacemos una aproximacion de montecarlo para ver que nuestra cartera sea realmente eficiente
#Simulamos pesos aleatorios, todos ellos deben caer debajo de la curva de la frontera eficiente, 
#es decir, que su varianza sea menor a la de la frontera eficiente para el mismo retorno esperado


N = 2000
lista_monteCarlo = []

# este comando da solamente los pesos que suman 1
pesos = np.random.dirichlet(np.ones(3), size=N)

for i in range(N):
    lista_monteCarlo.append((pesos[i][0], pesos[i][1], pesos[i][2]))

print(f"Se han generado numerosas combinaciones aleatorias de pesos para los activos. Total: {N} combinaciones.")
plt.figure()
plt.plot(E_vals, V_vals)

for i in range(len(lista_monteCarlo)):
    p1Carlo, p2Carlo, p3Carlo = lista_monteCarlo[i]
    E_random = m1*p1Carlo + m2*p2Carlo + m3*p3Carlo
    V_random = v1*p1Carlo**2 + v2*p2Carlo**2 + v3*p3Carlo**2 + 2*cv12*p1Carlo*p2Carlo + 2*cv13*p1Carlo*p3Carlo + 2*cv23*p2Carlo*p3Carlo
    plt.scatter(E_random, V_random, color='red', s=10, alpha=0.5)

plt.xlabel("Retorno esperado (E)")
plt.ylabel("Varianza (V)")
plt.title("Aproximacion de Montecarlo con combinaciones aleatorias de pesos")

plt.xlim(0, 0.15)
plt.ylim(0, 0.05)

plt.grid(True)

plt.savefig("aproximacion_montecarlo.png", dpi=300, bbox_inches="tight")
plt.show()

print("Es posible que el programa tarde o no termine bien, ya que la cantidad de combinaciones aleatorias es muy grande. haga crtl+c para detenerlo si es necesario.")