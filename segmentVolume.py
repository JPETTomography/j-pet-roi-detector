from volumeData import VolumeData
import lib
from skimage.filters import threshold_yen
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
import numpy as np
import os
import datetime

class SegmentVolume():
    """
    Obiekty tej klasy wykonują segmentacje różnymi metodami, a potem wyniki zapisuje do pliku.
    """
    # Gettery, prezentacja pól
    # Ścieżka z plikami po segmentacji
    @property
    def segmentDir(self):
        return self.__segmentDir

    # Surowe dane
    # Typ: VolumeData
    @property
    def rawVolume(self):
        return self.__rawVolume

    # Posegmentowane dane
    # Typ: VolumeData
    @property
    def segmentedVolume(self):
        return self.__segmentedVolume

    # Słownik działających algorytmów
    @property
    def algorithms(self):
        return self.__algorithms.keys()

    # Inicjalizator
    def __init__(self, inputData):
        """
        Konstruktor
        Sprawdza, czy nazwa algorytmu oraz dane są ok.
        """

        tempData = VolumeData(inputData)
        if tempData is not None:
            self.__rawVolume = tempData
        else:
            print('Niepoprawne dane!')
            raise ValueError

        # Stworzenie słownika z algorytmami
        algortihms = {'yen-thresh':__yenSegmentation, 'region-growing':__regionGrowingSegmentation, 'yen-region':__yenThreshRegionSegmentation, 'otsu-iter':__otsuIterSegmentation, 'otsu-multi':__otsuMultiSegmentation}
    
        # Ścieżka do pliku z wynikami segmentacji
        tempPath = './Segmentation_' + str(datetime.datetime.now().date())
        if os.path.exists(tempPath):
            num = 1
            while True:
                tempPathNum = tempPath + '_' + num
                if os.path.exists(tempPathNum):
                    num += 1
                else:
                    self.__segmentDir = tempPathNum
                    break
        else:
            self.__segmentDir = tempPath
        

    def segmentation(self, algName, params=None):
        """
        Wykonuje segmentację podanym algorytmem. Zapisuje zsegmentowane dane do pola segmentedVolume
        """
        if algName not in self.__algorithms.keys():
            print('Podano niepoprawny algorytm!')
            raise ValueError
        
        self.__segmentedVolume = self.__algorithms[algName](params)

    #--------------------------------------------------------------------
    # Algorytmy - metody prywatne
    #--------------------------------------------------------------------

    def __yenSegmentation(self, params):
        """
        Wykonuje segmentację metodą Yen'a

        Wartość zwracana
            Posegmentowana macierz 3D: VolumeData
        """
        thresh = threshold_yen(self._data3D)
        segVolume = self.__segmentDataByThresholds(thresh)

        return segVolume
    
    def __otsuIterSegmentation(self, iterCount=3):
        """
        Wykonuje segmentację algorytmem Otsu iteracyjnie
        Wartość zwracana
            Posegmentowana macierz 3D: VolumeData
        """
        thresh = 0
        threshList = []
        for i in range(iterCount):
            thresh = lib.threshOtsu(self._data3D, thresh)
            threshList.append(thresh)
        
        segVolume = self.__segmentDataByThresholds(threshList)
        print('Znalezione prgi: ', threshList)
        return segVolume
    
    def __regionGrowingSegmentation(self, startPoints, c=2, sigma0=20):
        """
        Wykonuje segmentację algorytmem Region Growing. Za punkt startowy bierze punkt z obszaru zsegmentowantego progowaniem Otsu.
        Wartość zwracana
            Posegmentowana macierz 3D: VolumeData
        """
        img = self.__rawVolume.data3D

        trzyDe = True
        if len(img.shape) == 2:
            trzyDe = False

        thresh = threshold_yen(img)
        bw = img >= thresh
        label_image = label(bw)

        centroidy = []
        for region in regionprops(label_image):
            centroidy.append(region.centroid)

        centroidy = np.array(centroidy)
        startPoints = np.around(centroidy).astype(int)
        regions = []
        for startPoint in startPoints:

            if startPoint is None:
                if trzyDe:
                    startPoint = [0,0,0]
                else:
                    startPoint = [0,0]

            # Parametr algorytmu
            c = 2

            region = [startPoint]

            # Transformacje, które pozwolą na multiindeksowanie macierzy/obrazu
            regionArr = np.array(region)
            if trzyDe:
                tempImg = img[regionArr[:,0], regionArr[:,1], regionArr[:,2]]
            else:
                tempImg = img[regionArr[:,0], regionArr[:,1]]

            avg = np.mean(tempImg)
            sigma0 = 20
            sigmaC = sigma0

            licznikTrafien = 0
            R = 1

            # Pętla po pikselach/wokselach. Wychodząc z punktu startPoint promieniście rozchodzi się algorytm.
            while(True):
                print(f'Promień: {R}')
                points = lib.pointsInRadius(startPoint, R)
                if not lib.belongsToArr(points, img):    # Sprawdzenie, czy przynajmniej jeden punkt należy do macierzy
                    print('Wyjście poza macierz wszystkich punktów.')
                    break

                licznikTrafien = 0
                for p in points:
                    # p - współrzędne punktu 
                    if lib.belongsToArr(p, img):
                        print(f'Punkt {p}: {img[p[0], p[1], p[2]]}')
                        if trzyDe:
                            tempWynik = abs(img[p[0], p[1], p[2]] - avg)
                        else:
                            tempWynik = abs(img[p[0], p[1]] - avg)
                        print(f'tempWynik: {tempWynik}, sigmaC: {sigmaC}')

                        if tempWynik <= sigmaC:
                            region.append(p)
                            print('Dodany')
                            licznikTrafien += 1

                            # Transformacje, które pozwolą na multiindeksowanie macierzy/obrazu
                            regionArr = np.array(region)
                            
                            if trzyDe:
                                tempImg = img[regionArr[:,0], regionArr[:,1], regionArr[:,2]]
                            else:
                                tempImg = img[regionArr[:,0], regionArr[:,1]]
        
                            avg = np.mean(tempImg)
                            sigmaC = c * np.sqrt(np.var(tempImg))

                            if sigmaC == 0:
                                sigmaC = sigma0
                
                            print('srednia:', avg)
                            print('sigma:', sigmaC)
                
                # Jeśli licznik jest 0 to zakończ pętlę
                if licznikTrafien == 0 :
                    print('Brak trafień dla promienia R=', R)
                    break

                R += 1
        r = np.array(region)
        regions.append(r)

        newImg = np.zeros(img.shape, dtype='uint8')

        for r in regions:
            if trzyDe:
                newImg[r[:,0], r[:,1], r[:,2]] = 255
            else:
                newImg[r[:,0], r[:,1]] = 255

        segImage = VolumeData(newImg)
        return segImage

    def __yenThreshRegionSegmentation(self, region_c=2, region_sigma0=20):
        img = self.__rawVolume.data3D
        thresh = threshold_yen(img)
        bw = img >= thresh
        label_image = label(bw)

        centroidy = []
        for region in regionprops(label_image):
            centroidy.append(region.centroid)

        centroidy = np.array(centroidy)
        startPoints = np.around(centroidy).astype(int)
        segImage = self.__regionGrowingSegment(startPoints, region_c, region_sigma0)

        return segImage

    def __otsuMultiSegmentation(self):
        """
        Segmentuje obraz za pomocą wielowartościowego (2) progowania Otsu.
        """
        thresholds = lib.multiThreshOtsu(self.__rawVolume.data3D)
        segImage = self.__segmentDataByThresholds(thresholds)
        return segImage

    def __segmentDataByThresholds(self, ths):
        """Segmentuje obraz 2d lub 3d w odniesieniu do progów podanych jako argumenty,
        Zwraca obiekt typu VolumeData
        """

        image = self._data3D
        maxThs = 8
        if not hasattr(ths, "__len__"):
            ths = [ths]

        if len(ths) > 1:
            ths = sorted(ths)   # Na wszelki wypadek sortowanko

        if len(ths) > maxThs:
            print('Nie obsługujemy tylu możliwych progów. Pozdrawiamy, ekipa segmentData.')
            return None

        # Kolory
        # kolory = []

        # Zmiana do kolorów w skali szarości
        kolory = np.linspace(0, 255, len(ths) + 1, dtype='uint8')   # Równo rozłożone wartości od czarnego do białego
        print('Kolory:', kolory)

        segData = np.zeros(image.shape, dtype='uint8')
    
        d0 = np.where(image < ths[0])    # Indeksy, dla których obraz ma wartość < ths[0]
        segData[d0] = kolory[0]

        for t in range(len(ths) - 1):
            logicTrue = np.logical_and(image >= ths[t], image < ths[t+1])
            di = np.where(logicTrue)
            segData[di] = kolory[t+1]

        dn = np.where(image >= ths[-1])
        segData[dn] = kolory[-1]
    
        return VolumeData(segData)

    # ---------------------------------------------
    # Pozostałe metody
    #----------------------------------------------

    def saveVolumeAsPickle(self, savePath = None):
        if savePath is None:
            savePath = self.__segmentDir + '/volumeData.pckl'
        self.__segmentedVolume.savePickle(savePath)

    def saveslicesAsPng(self, savepath = None):
        if savePath is None:
            savePath = self.__segmentDir + '/volumeSlices.png'
        


    



    