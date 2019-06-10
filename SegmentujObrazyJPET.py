"""
Main script. Supports UI.
Główny plik projektu. Obsługuje komunikację z użytkownikiem 
"""

from lib import *
from segmentVolume import SegmentVolume
import argparse
import json

# Define parser
parser = argparse.ArgumentParser(description=TEKST_POWITALNY, formatter_class=argparse.RawDescriptionHelpFormatter)

# Positional arguments - algorithm i datapath
parser.add_argument('alg', metavar='ALGORITHM', type=str, help=INFO_ALG)
parser.add_argument('dataPath', metavar='PATH_TO_DATA', type=str, help=INFO_DATA)

# Optional arguments
parser.add_argument('--savePickle', action='store_true', help=INFO_SAVE_PICKLE)
parser.add_argument('--saveSlices', action='store_true', help=INFO_SAVE_SLICES)
parser.add_argument('--algParams', metavar=' KEYWORD_PARAMS_TO_ALG', type=json.loads)       # json/dict arguments

# Main
args = parser.parse_args()
# print('Podano:', args)      
segObj = SegmentVolume(args.dataPath)
segObj.segmentation(args.alg, args.algParams)
if args.savePickle:
    segObj.saveVolumeAsPickle() 
      
if args.saveSlices:
    segObj.saveSlicesAsPng()


