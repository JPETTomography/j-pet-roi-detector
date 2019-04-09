import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib
from lib import VolumeData, vol2Img3D, arr2img
from scipy.signal import argrelmin
"""
1. Wczytanie obrazu fantoma z pliku i pobranie slice'u (przekroju)
2. Progowanie:
   - wyciąganie progów z (wygładzonego) histogramu
   - progowanie adaptacyjne
   - progowanie iteracyjne
4. Wykrywanie krawędzi
"""

# 1. Wczytanie i wyświetlenie przekrojów fantoma

FantomPath = '/home/krzysztof/Dokumenty/Praca_inż/j-pet-roi-detector/Fantom'
dataFilePath = FantomPath + '/data.pckl'

fantomVolume = VolumeData(dataFilePath)
# fantomVolume.showAllSlicesInOne()     # Prezentacja wszystkich przekrojów obok siebie
sliceNum = 16
slice2d = fantomVolume.getSlice(sliceNum)
# plt.imshow(slice2d)                   # Prezentacja pojedynczego przekroju
# plt.show()


# 2. Implementacja algorytmu segmentującego przez progowanie

# Histogram próbek
# bins - równoodległe punkty na osi x
binsCount = 2000
bins = np.arange(0, 1, 1/binsCount)
hist, edges = np.histogram(slice2d, bins=bins)
# Wygładzenie histogramu
dlug_okna = int(0.05*binsCount)
hist_mean = np.convolve(hist, np.ones((dlug_okna,))/dlug_okna, mode='valid')
xx = np.linspace(0, 1, len(hist_mean))

plt.figure(1)
plt.plot(xx, hist_mean)
# plt.yscale('log')
plt.show()
# Progowanie ręczne - trzeba będzie zrobić to metodą Otsu
# Będą trzy progi 
p1 = 0.08
p2 = 0.38
p3 = 0.47
p4 = 0.59

img2 = np.zeros([121,121,3])

for i in range(121):
    for j in range(121):
        if slice2d[i,j] < p1:
            img2[i, j, :] = [0.0, 0.0, 0.0]
        elif slice2d[i,j] >= p1 and slice2d[i,j] < p2:
            img2[i, j, :] = [0.0, 0.0, 255.0]
        elif slice2d[i,j] >= p2 and slice2d[i,j] < p3:
            img2[i, j, :] = [0.0, 255.0, 0.0]
        elif slice2d[i,j] >= p3 and slice2d[i,j] < p4:
            img2[i, j, :] = [255.0, 0.0, 0.0]
        else:
            img2[i, j, :] = [255.0, 255.0, 255.0]

plt.figure(2)
plt.imshow(img2)
plt.title('Wynik segmentacji po ręcznym wyborze progów')
plt.show()


# Jak dobrać parametr bins ?
# Histogram dzieli zakres maksymalnych 
"""
arr = np.random.rand(100,100)
bins = np.arange(0,1,0.001)
hista, bin_edges = np.histogram(arr, bins=10)
plt.plot(hista,'ro')
plt.show()
"""