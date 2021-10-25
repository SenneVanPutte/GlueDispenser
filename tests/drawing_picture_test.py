import sys
import time
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue-no-timeout')

import matplotlib
from matplotlib import pyplot
#from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation

def func_str(str):
	print(str)
	
	
if __name__ == '__main__':
	dr = drawing2('../drawings/kapton_pigtail.dxf')
	dr.get_picture_locations('kapton_picture')