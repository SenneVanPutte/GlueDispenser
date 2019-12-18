import sys
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')

import matplotlib
from matplotlib import pyplot
#from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation

	
if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	
	scale = scale_handler()
	scale.zero()
	scale.calibrate()