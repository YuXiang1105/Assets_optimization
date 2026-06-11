import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

m1 = 0.1180850933 #IBEX35
m2 = 0.1619481497 #SP500
m3 = 0.0771816605 #EMM
v1 = 0.03492332644
v2 = 0.02776645397
v3 = 0.03505910984
cv12 = 0.001666029016
cv13 = 0.0005078163229
cv23 = 0.0005112105901

# Gröbner se calcula UNA sola vez
p1, p2, E, V = sp.symbols('p1 p2 E V', real=True)
p3 = 1 - p1 - p2
# Definimos las ecuaciones polinomiales para la frontera eficiente
# Se tienen que igualar a 0, se pasan al otro lado de la igualdad
pol2 = E - (m1*p1 + m2*p2 + m3*p3)
pol3 = V - (v1*p1**2 + v2*p2**2 + v3*p3**2 +
            2*cv12*p1*p2 + 2*cv13*p1*p3 + 2*cv23*p2*p3)

# Creamos el sistema de ecuaciones polinomiales y calculamos el Gröbner
G = sp.groebner([pol2, pol3], p1, p2, E, V, order='lex')
eq1, eq2 = G[0], G[1] # Sacamos los dos elementos del ideal

# Resolvemos el sistema de ecuaciones polinomiales para p1 y p2 en función de E y V usando la base
# Nos quedaramos con la primera solución, ya que la segunda es la misma pero con p1 y p2 intercambiados, lo que no aporta nada nuevo a la frontera eficiente
# Esta solucion, reduciendo con la base de grobner hará que cada elemento del ideal solo dependa de p1 o p2, facilitando los calculos
p1_expr = sp.solve(eq1, p1)[0]
eq2_sub = sp.simplify(eq2.subs(p1, p1_expr))
sol_p2 = sp.solve(eq2_sub, p2)
p2_sol_a = sol_p2[0]
p2_sol_b = sol_p2[1]

p1_sol_a = sp.simplify(p1_expr.subs(p2, p2_sol_a))  # p1 correspondiente a sol a
p1_sol_b = sp.simplify(p1_expr.subs(p2, p2_sol_b))  # p1 correspondiente a sol b

# Realizaremos un bucle, para aproximar E y V, y asi obtener los pesos de cada activo para cada punto de la frontera eficiente, quedandonos con el punto de menor varianza para cada valor de E
MenoresVarianzas = []
Esperanzas = []

# Discretizacion de la varianza
recorrer = np.linspace(0.01, 0.04, 1000)

# Las esperanzas tienen que estar entre la rentabilidad minima y maxima, si no, no se pueden calcular los pesos de cada activo, ya que no se pueden obtener soluciones reales para p1 y p2
E_min = min(m1, m2, m3)
E_max = max(m1, m2, m3)

E_vals = np.linspace(float(E_min), float(E_max), 1000)
for E_valor in E_vals:
    # Sustituimos los valores de E
    p1_a_E = p1_sol_a.subs(E, E_valor)
    p1_b_E = p1_sol_b.subs(E, E_valor)
    p2_a_E = p2_sol_a.subs(E, E_valor)
    p2_b_E = p2_sol_b.subs(E, E_valor)
    
    f_p1_a = sp.lambdify(V, p1_a_E, "numpy")
    f_p1_b = sp.lambdify(V, p1_b_E, "numpy")
    f_p2_a = sp.lambdify(V, p2_a_E, "numpy")
    f_p2_b = sp.lambdify(V, p2_b_E, "numpy")

    V_frontera, p1_f, p2_f, p3_f = [], [], [], []

    for V_valor in recorrer:
        for (fa, fb) in [(f_p1_a, f_p2_a), (f_p1_b, f_p2_b)]:
            try:
                # Pasamos los valores a tipo float y calculamos el peso 3, que era dependiente de los otros 2 por la reestriccion
                pol1It = float(np.real(fa(V_valor)))
                pol2It = float(np.real(fb(V_valor)))
                pol3It = 1 - pol1It - pol2It
                if (np.isfinite(pol1It) and np.isfinite(pol2It) and np.isfinite(pol3It) and pol1It >= 0 and pol2It >= 0 and pol3It >= 0):
                # Ponemos la reestriccion de que los pesos no pueden ser negativos, ya que sino el inversor estaria vendiendo el activo
                    V_frontera.append(V_valor)
                    # Guardamos los pesos
                    p1_f.append(pol1It)
                    p2_f.append(pol2It)
                    p3_f.append(pol3It)
            except:
                # Si da un fallo, saltamos a la siguiuente iteracion, que puede ocurrir si una de las reestricciones no se cumple
                continue

    if V_frontera:
        # Guardamos el punto de menor varianza para cada valor de E, que es el punto de la frontera eficiente
        i = np.argmin(V_frontera)
        # Guardamos el valor n veces, el nhumero de iteraciones
        MenoresVarianzas.append([E_valor, V_frontera[i], p1_f[i], p2_f[i], p3_f[i]])
        Esperanzas.append(E_valor)
        # Aumentamos E para la siguiente iteracion

# Cambiamos a formato [(Esperanza,Varianza)] para facilitar los graficos
frontera = list(zip(Esperanzas, MenoresVarianzas))
print(frontera)

E_vals = []
V_vals = []

# Sacamos los valores de E y V para graficar la frontera eficiente en un array, para el formato de matplotlib
for row in MenoresVarianzas:
    E_vals.append(row[0])FronteraEficiente3IndicesETF
    V_vals.append(row[1])

E_vals = np.array(E_vals)
V_vals = np.array(V_vals)

# Ordenar por E y V, deberian ya estar ordenados, pero por si acaso
idx = np.argsort(E_vals)
E_vals = E_vals[idx]
V_vals = V_vals[idx]

# Hacer el plot de la frontera eficiente, con el conjunto de Esperanzas y Varianzas 
plt.figure()
plt.plot(E_vals, V_vals)

plt.xlabel("Retorno esperado (E)")
plt.ylabel("Varianza (V)")
plt.title("Frontera eficiente")

plt.xlim(0, 0.2)
plt.ylim(0, 0.05)

plt.grid(True)

plt.savefig("frontera_eficiente.png", dpi=300, bbox_inches="tight")
plt.show()

# Hacemos una aproximacion de montecarlo para ver que nuestra cartera sea realmente eficiente
# Simulamos pesos aleatorios, todos ellos deben caer debajo de la curva de la frontera eficiente, es decir, que su varianza sea menor a la de la frontera eficiente para el mismo retorno esperado

print("Realizaremos una aproximacion de MonteCarlo, es posible que el programa tarde o no termine bien, ya que la cantidad de combinaciones aleatorias es muy grande. Haga crtl+c para detenerlo si es necesario.")
N = 2000
lista_monteCarlo = []

# Este comando da solamente los pesos que suman 1 y nos da valores aleatorios, que son carteras aleatorias
pesos = np.random.dirichlet(np.ones(3), size=N)

# Guardamos los pesos
for i in range(N):
    lista_monteCarlo.append((pesos[i][0], pesos[i][1], pesos[i][2]))
# Print para el tamaño, y ademas debbing para ver que se estan generando las combinaciones
print(f"Se han generado numerosas combinaciones aleatorias de pesos para los activos. Total: {N} combinaciones.")
plt.figure()
plt.plot(E_vals, V_vals)

# Calulamos el retorno esperado y la varianza para cada combinacion de pesos, y los graficamos, para ver que caen debajo de la frontera eficiente
for i in range(len(lista_monteCarlo)):
    p1Carlo, p2Carlo, p3Carlo = lista_monteCarlo[i]
    E_random = m1*p1Carlo + m2*p2Carlo + m3*p3Carlo
    V_random = v1*p1Carlo**2 + v2*p2Carlo**2 + v3*p3Carlo**2 + 2*cv12*p1Carlo*p2Carlo + 2*cv13*p1Carlo*p3Carlo + 2*cv23*p2Carlo*p3Carlo
    plt.scatter(E_random, V_random, color='red', s=2, alpha=0.5)

# Hacemos el plot similar anterior, pero con un scatterplot (puntos de (E,V)) para ver que se aproxima bien
plt.xlabel("Retorno esperado (E)")
plt.ylabel("Varianza (V)")
plt.title("Aproximacion de Montecarlo con combinaciones aleatorias de pesos")

plt.xlim(0, 0.2)
plt.ylim(0, 0.05)

plt.grid(True)

plt.savefig("aproximacion_montecarlo.png", dpi=300, bbox_inches="tight")
plt.show()

# Exportamos con pandas a un excel
tabla = pd.DataFrame(MenoresVarianzas, columns=['Rentabilidad', 'Varianza', 'IBEX35', 'SP500', 'EMM'])
tabla['Rentabilidad'] = tabla['Rentabilidad']
tabla['Varianza'] = tabla['Varianza'].round(6)
tabla['SP500'] = tabla['SP500'].round(4)
tabla['IBEX35'] = tabla['IBEX35'].round(4)
tabla['EMM'] = tabla['EMM'].round(4)

print(tabla.to_string(index=False))
tabla.to_excel("Discretizacion.xlsx", index=False)