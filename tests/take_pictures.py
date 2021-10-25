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
	cv2.imwrite(output_dir+name, image)

# Kapton	
coo_list = [[-10, -5], [-10, 90], [40, 85], [80, 0], [80, 90]]
pic_tag = 'kapton_on_jig'
# Test pcb
#coo_list = [[-10, -5], [22.5, -5], [55,-5]]
#coo_list = [[-28, -19], [4.5, -19], [37,-19]]
#pic_tag = 'test_pcb'

pause_time = 1
	
if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.home()
	##machiene.init_code()
	
	for iPic in range(1):
	
		for coo in coo_list:
			machiene.gotoxy(coo[0], coo[1])
			x_str = str(coo[0])
			y_str = str(coo[1])
			time_str = datetime.datetime.now().strftime("%Y_%b_%d_at_%H_%M_%S")
			pic_name = pic_tag+'_x_'+x_str+'_y_'+y_str+'_'+time_str+'.png'
			time.sleep(0.5)
			take_picture(webcam, pic_name)
			time.sleep(0.5)
		time.sleep(pause_time)
			
		
	
	machiene.gotoxy(300, 300)
		