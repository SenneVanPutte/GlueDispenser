from scale_handler import scale_handler, measure_delay, delay_and_flow_regulation, delay_and_flow_regulation2
from gcode_handler import gcode_handler, drawing
import time

import matplotlib
from matplotlib import pyplot

if __name__ == '__main__':
	machiene = gcode_handler()
	#machiene.init_code()
	
	scale = scale_handler() 
	scale.init_glue_log()
	#time.sleep(3)
	scale.zero()
	start = time.time()
	while time.time() - start < 4:
		print(scale.read_mass())
		time.sleep(0.5)
	#scale.send_command("t")
	while(1):
		print(scale.read_mass())
		time.sleep(0.5)
	#scale.send_command("t")
	time.sleep(5)
	
	