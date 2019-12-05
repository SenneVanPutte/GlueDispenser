Script to convert dots placed in DXF file to movements of a liteplacer pick and place machine.

Depends on:
- ezdxf
- pyserial

DXF file convention:
- dots must de draw as points in layer "points"
- layer "border" contains the contour of the sensor (test purpose)

LitePlacer G-code and commands:
https://github.com/synthetos/TinyG/wiki/TinyG-Configuration-for-Firmware-Version-0.97