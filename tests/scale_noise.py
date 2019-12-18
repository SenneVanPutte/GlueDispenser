import sys
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')

import datetime
import matplotlib
from matplotlib import pyplot
#from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation

noise_file = 'tests\\scale_noise.txt' 

def write_data_to_file(data, file_name):
	x_raw = []
	y_raw = []
	data_file_o = open(file_name, 'w')
	data_file_o.write("#\t ____START_NOISE_SESSION____\n")
	data_file_o.write("#\t TIME: " + datetime.datetime.now().strftime("%Y %b %d\t%H:%M:%S") + "\n")
	for entry in data:
		x_raw.append(entry[0])
		y_raw.append(entry[1][0])
		prt_str = '\t'.join([str(entry[0]), str(entry[1][0]), '\n'])
		data_file_o.write(prt_str)
	data_file_o.close()
	
	
def read_data(file_name):
	file_o = open(file_name, 'r')
	lines = file_o.readlines()
	file_o.close()
	
	x_raw = []
	y_raw = []
	for line in lines:
		if '#' in line: continue
		line_content = line.replace('\n', '').split('\t')
		time = float(line_content[0])
		mass = float(line_content[1])
		x_raw.append(time)
		y_raw.append(mass)
		
	x_st = min(x_raw)
	x_rel = [val - x_st for val in x_raw]
	
	m_f = 1000
	y_mean = sum(y_raw)/float(len(y_raw))
	y_rel = [(val - y_mean)*m_f for val in y_raw]
	
	pyplot.hist(y_rel, 50, density=True)
	pyplot.xlabel('Delta mass (mg)')
	pyplot.ylabel('Probability')
	pyplot.title('Scale Noise')
	pyplot.show()
	
	
if __name__ == '__main__':
	#machiene = gcode_handler()
	#machiene.init_code()
	
	scale = scale_handler()
	scale.zero()
	scale.calibrate()
	
	duration = 600
	print('Listen to noise for ' + str(duration) + ' s')
	data = scale.read_out_time(duration, record=True)
	scale.plot_data(data)
	
	write_data_to_file(data, noise_file)
	read_data(noise_file)