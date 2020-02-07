from scale_handler import scale_handler, measure_delay, delay_and_flow_regulation, ts_to_timestr
from gcode_handler import gcode_handler, drawing
from glueing_cfg import DRAWING_CFG, JIG_CFG, GRID_CFG
import time

import matplotlib
from matplotlib import pyplot

def imp():
	from glueing_cfg import DRAWING_CFG, JIG_CFG, GRID_CFG
	print(GRID_CFG)

if __name__ == '__main__':
	print(GRID_CFG)
	imp()
	imp()
	# machiene = gcode_handler()
	#machiene.init_code()
	
	# scale = scale_handler() 
	# scale.init_glue_log()
	#time.sleep(3)
	# scale.zero()
	# start = time.time()
	# while time.time() - start < 4:
		# print(scale.read_mass())
		# time.sleep(0.5)
	#scale.send_command("t")
	# while(1):
		# print(scale.read_mass())
		# time.sleep(0.5)
	#scale.send_command("t")
	# time.sleep(5)
	print(ts_to_timestr(time.time()))
	
	