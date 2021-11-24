# AirBraille

AirBraille is a prototype written in Python that aims to provide an alternative way to input Braille on a computer by using a camera that focuses the user's hands and evaluates the position of the fingers.

## Usage
```python
from AirBraille import *

# init
air_braille = AirBraille(your_writehandler)

# start the detection
air_braille.start_detection()
```