import sys
import time
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')

import matplotlib
from matplotlib import pyplot
#from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation

def func_str(str):
	print(str)
	
	
if __name__ == '__main__':
	machiene = gcode_handler()
	#machiene.init_code()
	#machiene.reconfigure()
	machiene.set_pressure(3000., no_flush=False)
	time.sleep(10)
	machiene.stop_pressure()
	
	# scale = scale_handler()
	# scale.zero()
	# scale.calibrate()
	
	#func_str()