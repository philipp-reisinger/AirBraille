# This script starts the detection.

from AirBraille import *
from WriteHandler import *

# sources
six_dot_file = "braille_files/6_dot_AT.json" # https://fakoo.de/braille/braille-alphabet.html?mi2
eight_dot_file = "braille_files/8_dot_AT.json" # https://fakoo.de/computerbraille.html

if __name__ == '__main__':
    air_braille = AirBraille(WriteHandler6Dot(six_dot_file))
    air_braille.start_detection()
