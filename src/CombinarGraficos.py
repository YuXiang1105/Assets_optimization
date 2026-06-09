#Este archivo es para comparar implementaciones, para ver si el resultado es el mismo,
#y para comparar los graficos de la frontera eficiente, para ver si son iguales
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#leemos imagenes
img1 = mpimg.imread("Optimizacion cuadratica.png")
img2 = mpimg.imread("frontera_eficiente.png")

plt.figure(figsize=(8,6))
#Combinamos
plt.imshow(img1, alpha=1.0)   # imagen base
plt.imshow(img2, alpha=0.5)   # imagen superpuesta con transparencia

plt.axis("off")
plt.show()
