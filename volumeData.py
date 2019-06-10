import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
# import random
# import itertools
# from timeit import default_timer as timer
import lib
# import datetime

class VolumeData():
    """
    Obiekty tej klasy wykonują operacje na plikach z rekonstrukcji (odczyt, zapis do pliku).
    Dozwolone formaty plików: 
    - tekstowy .txt
    - pickle .pckl - wygodny format zapisu ZMIENNYCH do pliku w Pythonie
    
    Dane mogą być podane jako:
    - macierz N x 4 - kolumny to {x, y, z, intensywność}, a wiersze to kolejne pomiary
    - obrazy {x,y,z} (macierze 3D)  
    
    Obrazy można zapisać do plików pickle jako macierze 3D
    Obiekty posiadają atrybuty:
    - data3D - macierz punktów 3D
    - fileName - końcowa nazwa pliku

    Obiekty posiadają metody:
    - init(filePath) - konstruktor. Jako argument podawana jest ścieżka do pliku.
    - savePickle(filePath) - zapis danych (macierz 3D) do pliku pickle pod zadaną nazwą
    - getSlice(sliceNUM) - zwraca macierz 2D (obraz) konkretnego przekroju
    - showAllSlicesInOne() - wyświetla wszystkie przekroje obok siebie na jednym figure 
    """

    
    @property
    def data3D(self):
        return self._data3D

    @property
    def dataName(self):
        return self._dataName
    
    def __init__(self, inputData, dataType='uint8'): 
        """
        Tworzy obiekt data3D przechowujący obraz 3D z tomografu.

        Argumenty

            inputData (string lub array): Dane wejściowe. Mogą pochodzić z:
            - pliku txt lub pickle
            - macierzy Nx4 (x, y, z, f{x,y,z}) lub PxQxR

            dataType (string): do wyboru:
            - 'float' - dane formatowane do flaot 32 bitowego, wartości z przedziału [0,1] - narazie brak
            - 'uint8' - format 8 bitowy, dane z przedziału [0,255]
        
        """
        # Do zaimplementowania - różne typy danych. W sumie lepiej jak będzie uint8 - znana z góry liczba możliwych wartości
        # Trzeba też uwzględnić możliwość tworzenia obiektów na podstawie macierzy
        rawdata = []

        # Użytkownik podał ścieżkę do pliku
        if isinstance(inputData, str):
            ext = os.path.splitext(inputData)[1]     # Pobranie nazwy pliku i rozszerzenia
            if ext == '.pckl':
                print('Wczytuję dane z pliku pckl...')
                try:
                    rawData = np.load(inputData)
                except FileNotFoundError:
                    raise ValueError

            elif ext == '.txt':
                print('Wczytuję dane txt...')
                try:
                    rawData = np.loadtxt(inputData)
                except FileNotFoundError:
                    raise ValueError

            else:
                print('Niepoprawna ścieżka do pliku z danymi. Dozwolone są ścieżki z rozszerzeniami .txt lub .pckl')
                raise ValueError
            
            self._dataName = os.path.basename(os.path.normpath(inputData))

        # Użytkownik podał macierz 
        elif isinstance(inputData, np.ndarray):
            print('Wczytuję dane z macierzy...')
            rawData = inputData
            self._dataName = "Dane"

        # Jeśli nie podano macierzy ani ścieżki
        else:
            print(f'Zły typ danych wejściowych inputData. Oczekiwane: numpy.array lub str. Podano {type(a)}.')
            raise ValueError

        # Formatowanie danych do macierzy 3D uint8
         
        ksztalt = rawData.shape
        if len(ksztalt) == 2:
            if ksztalt[0] > 0 and ksztalt[1] == 4:      # Dane w formacie Nx4
                rawData = lib.points2Img3D(rawData)
                print('Konwersja do wolumenu 3D')
            else:
                print('Niepoprawny format danych.')
                raise ValueError

        elif len(ksztalt) == 3:
            print('Brak konwersji - dane w formacie 3D')
            
        else:
            print('Niepoprawny format danych. Wymagany Nx4 lub KxLxM')
            raise ValueError

        print(f'Dane mają wymiary: {rawData.shape}')

        # Convert to uint8, in future version - float
        if isinstance(rawData.flat[0], np.float):
            if np.min(rawData) >= 0 and np.max(rawData) <= 1:
                print('Konwersja danych do uint8')
                rawData = np.array(255*rawData, dtype='uint8')
            else:
                print('Niepoprawny typ danych. Wymagany np.float (wartości 0-1 lub np.integer 0-255)')
                raise ValueError

        elif isinstance(rawData.flat[0], np.integer) or isinstance(rawData.flat[0], np.uint8):
            if np.min(rawData) >= 0 and np.max(rawData) <= 255:
                rawData = np.array(rawData, dtype='uint8')
            else:
                print('Niepoprawny typ danych. Wymagany np.float (wartości 0-1 lub np.integer 0-255)')
                raise ValueError

        self._data3D = rawData


    def savePickle(self, filePath):    
        "Zapisuje dane jako plik pickle"
        with open(filePath, 'wb') as f:
	        pickle.dump(self._data3D, f)

    def saveSlices(self, filePath, title='Segmentacja'):
        fig = self.__makeFigureWithAllSlices(figTitle=title)
        fig.savefig(filePath)

    def getSlice(self, sliceNum=None, deep=None):     
        "sliceNum - numer przekroju, deep - 'głębokość w objętości podana jako liczba z przedziału (0,1)"
        if sliceNum != None and deep == None:
            return self._data3D[:,:,sliceNum]
        elif deep != None and sliceNum == None:
            sliceNum = int(deep * self._data3D.shape[2])
            return self._data3D[:,:,sliceNum]
        else:
            print('getSlice: Niepoprawna liczba argumentów')

    def __makeFigureWithAllSlices(self, size = (20,20), figTitle = None):
        if figTitle == None:
            figTitle = self._dataName
        Nz = self._data3D.shape[2]   # Liczba przekrojów
        maxValue = np.amax(self._data3D)
        minValue = np.amin(self._data3D)
        rows = int(np.sqrt(Nz))
        cols = Nz//rows + 1
        fig = plt.figure(figsize=size)
        fig.suptitle(figTitle, fontsize=20)

        for index in range(0,Nz):
            ax = fig.add_subplot(rows,cols,index+1)
            ax.imshow(self.getSlice(sliceNum=index), vmin=minValue, vmax=maxValue)
            ax.set_title( index )
            frame = plt.gca()
            frame.axes.get_xaxis().set_visible(False)
            frame.axes.get_yaxis().set_visible(False)
        

        return fig

    def showAllSlices(self, title = None):
        "Tworzy kolarz ze wszystkich przekrojów wolumenu"
        if title == None:
            title = self._dataName
        # Niech będzie 6 rzędów
        fig = self.__makeFigureWithAllSlices()
        
        plt.show()
        fig.savefig()
        
        return self._dataName

