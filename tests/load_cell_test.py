import os
import cv2
import sys
import time
import datetime
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')
from gcode_handler import gcode_handler

SCALE_POSITION = [350, 200]

	
if __name__ == '__main__':
	machine = gcode_handler()
	machine.init_code()
	
	machine.gotoxy(SCALE_POSITION[0], SCALE_POSITION[1])
	
	scale_h = machine.probe_z(speed=25, up=0)
	
	print('Read loading cell and scale value')
	print('Should be relatively close')
	
	#machine.down(scale_h - 1)
	#machine.down(scale_h + 0.05, speed=25)
	
	
	
	