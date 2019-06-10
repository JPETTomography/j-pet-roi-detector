# j-pet-roi-detector
English below.

Projekt dotyczący znajdowania obszarów zaintersowania (ROI) w obrazach trójwymiarowych pochodzących z tomografu PET, a konkretnie z rekonstrukcji po skanowaniu.

Segmentacja wykonywana jest następującymi metodami:
- progowanie ręczne - analityk sam dobiera progi, a następnie dzieli obraz na obsary pod względem progów(?)
- progowanie Otsu iteracyjne
- progowanie Otsu wielowartościowe
- progowanie Yena
- progowanie Yena + Region Growing

Organizacja projektu:
* Program główny i komunikacja z użytkownikiem znajduje się w pliku SegmentujObrazyJPET.py
* W pliku volumeData.py znajduje się implementacja klasy VolumeData, która odpowiada za operacje na obrazie, w tym:
  - wczytywanie obrazu z pliku tekstowego oraz pckl lub z macierzy
  - segmentacja wyżej wymienionymi algorytmami
  - wyświetlenie przekrojów obrazu
  - wyświetlenie pojedynczego przekroju
  - zapis obrazu do pliku
* W pliku lib.py znajdują się pozostałe użyteczne funkcje oraz zmienne typu string z tekstami wyświetlanymi użytkownikowi
* Pakiety potrzebne do uruchomienia programu znajdują się w pliku requirements.txt

Program uruchamia się wywołując skrypt SegmentujObrazyJPET.py - python SegmentujObrazyJPET.py. Spowoduje to wywołanie interaktywnej mini konsoli do komunikacji z użytkownikem.

#########
 English
#########

The aim of the project is to find Regions Of Interest (ROI) on volumes created during reconstruction of PET Tomography imaging.

Segmentation will be done by the following methods:
- manual thresholding - the anlalyst finds thresholds with his knowledge and experience
- iterative Otsu thresholding
- multiple Otsu thresholding
- Yen thresholding
- Yen thresholding + Region Growing

Project files
* Main program with console UI is located in SegmentujObrazyJPET.py file
* In the file volumeData.py there is an implementation of VolumeData class, which contains methods such as:
    - load volume from file (.txt or pickle) or array
    - segment images 
    - plot volume or single slices
    - save volume to a pickle file
