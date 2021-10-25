import os
import cv2
import sys
import time
import datetime
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')
from gcode_handler import gcode_handler


webcam = cv2.VideoCapture(2)

def take_picture(webcam, name, output_dir='C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\'):
	success, image = webcam.read()
	success, image = webcam.read()
	cv2.imwrite(output_dir+name, image)
	
	
	
square = [[0, 0], [100, 0], [100, 100], [0, 100]]
offset = [40, 15]
pic_tag = 'kapton_on_jig'

def square_test(machine, webcam, pic_tag, offset, square, pause=0, iterations=10):
	for it in range(iterations):
		print('Starting iteration: '+str(it))
		it_tag = 'it_'+str(it)
		#machine.home()
		time_str = datetime.datetime.now().strftime("%Y_%b_%d")
		pic_name = '_'.join([pic_tag, it_tag, 'home', time_str])+'.png'
		#take_picture(webcam, pic_name)
		for corner in square:
			x = corner[0] + offset[0]
			y = corner[1] + offset[1]
			pos_tag = 'x_'+str(x)+'_y_'+str(y)
			timing_tag = 'before'
			time_str = datetime.datetime.now().strftime("%Y_%b_%d")
			machine.gotoxy(x,y)
			pic_name = '_'.join([pic_tag, it_tag, timing_tag, pos_tag, time_str])+'.png'
			take_picture(webcam, pic_name)
			time.sleep(pause)
			timing_tag = 'after'
			pic_name = '_'.join([pic_tag, it_tag, timing_tag, pos_tag, time_str])+'.png'
			take_picture(webcam, pic_name)
	
	
if __name__ == '__main__':
	machine = gcode_handler()
	##machine.init_code()
	
	
	machine.init_code()
	print('homing done')
	machine.gotoxy(100, 100)
	print('moving done')
	#machine.send_bloc('''
	#$mt=3600; set timeout in seconds
	#''')
	machine.send_bloc('''
	$mt; set timeout in seconds
	''')
	machine.probe_z(speed=100)
	
	#$1pm=1; set motor 1 always on (0 always off, 1 always on, 2 timeout enabled)
	#machine.home()
	#square_test(machine, webcam, 'square_test_pause_nohoming', offset, square, pause=2, iterations=10)
	
	