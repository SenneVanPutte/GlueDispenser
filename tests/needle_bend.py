import sys
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')

import math
import scipy
import datetime
import matplotlib
from matplotlib import pyplot
#from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation
from scale_handler import lin_reg

#data_file = 'tests\\NeedleBend_blue_metal.txt'
#data_file = 'tests\\NeedleBend_pink_metal.txt'
data_file = 'tests\\NeedleBendLC2_blue_metal.txt'

#data_file = 'tests\\NeedleBend_pink_plastic.txt'

def read_file(file_name, write_cache=False):
	file_o = open(file_name, 'r')
	lines = file_o.readlines()
	file_o.close()
	
	data = {}
	speed_lst = []
	for line in lines:
		if '#' in line: continue
		line_content = line.replace('\n', '').split('\t')
		speed = float(line_content[0])
		p0 = float(line_content[1])
		if speed not in data:
			data[speed] = {}
			data[speed]['p'] = []
			speed_lst.append(speed)
		data[speed]['p'].append(p0)
		
	
	for spd in data:
		data[spd]['mean'] = sum(data[spd]['p'])/float(len(data[spd]['p']))
		
		var_lst = []
		for pt in range(len(data[spd]['p'])):
			var_lst.append((data[spd]['p'][pt] - data[spd]['mean'])**2)
		var = sum(var_lst)/float(len(var_lst))
		std = math.sqrt(var)
		
		data[spd]['std'] = std
		
	speed_lst.sort()
	std_lst = []
	relmean_lst = []
	factor = 1000.
	for spd in speed_lst:
		std_lst.append(data[spd]['std']*factor)
		relmean_lst.append((data[spd]['mean'] - data[speed_lst[0]]['mean'])*factor)
		
	
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, std_lst, label='std ref point')
	ax.set(xlabel='Speed (mm/min)', ylabel=u'Hight std (\u03bcm)', title='Bend std')
	pyplot.show()
	
	mass_w = [1./(std**2) for std in std_lst]
	bias, bend_f, bias_int, bf_int, failed = lin_reg(speed_lst, relmean_lst, mass_w)
	print(bias, bend_f)
	bend_fit = [s*bend_f + bias for s in speed_lst]
	
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, relmean_lst, label='mean')
	ax.plot(speed_lst, bend_fit, 'r--', label='fit')
	ax.plot(speed_lst, sum_lists(relmean_lst, std_lst), 'c--', label='mean + std')
	ax.plot(speed_lst, sum_lists(relmean_lst, std_lst, factor=-1), 'c--', label='mean - std')
	ax.legend()
	ax.set(xlabel='Speed (mm/min)', ylabel=u'Relative Hight (\u03bcm)', title='Bend')
	#ax.set_xscale('log')
	#ax.set_yscale('log')
	pyplot.show()
	
	ms = ((-bias)/(60.*bend_f))*1000.
	print('Equivalent to ' + str(ms) + ' ms of movement')
	
	if write_cache:
		splt_name = file_name.split('_')
		cache_file = 'cache\\NeedleBendVar_'+splt_name[-2]+'_'+splt_name[-1]
		print('Writing fit to ' +cache_file)
		file_o = open(cache_file, 'w')
		file_o.write('#\t ' + splt_name[-2]+'_'+splt_name[-1] + '\n')
		file_o.write('rico:\t' + str(bend_f/factor) + '\n')
		file_o.write('bias:\t' + str(bias/factor) + '\n')
		file_o.close()
	
def sum_lists(x, y, factor=1):
	z = [x[i] + factor*y[i] for i in range(len(x))]
	return z

#def write_bend_correction_file(speed, bend, file_name):
#	bias, bend_f, bias_int, bf_int, failed = lin_reg(speed, bend)
	
	
	
if __name__ == '__main__':

	measure = False
	
	if not measure:
		read_file(data_file, False)
		exit()

	machiene = gcode_handler()
	machiene.init_code()
	
	data_file_o = open(data_file, 'a')
	data_file_o.write("#\t ____START_BEND_SESSION____\n")
	data_file_o.write("#\t TIME: " + datetime.datetime.now().strftime("%Y %b %d\t%H:%M:%S") + "\n") #%G %b %d  
	data_file_o.close()
	
	prb_speeds = [200, 175, 150, 125, 100, 50, 25, 12, 6]
	#prb_speeds = [125, 100]
	probe_pos = [36, 110]
	#prb_speeds = [175, 125, 12, 6]
	machiene.gotoxy(probe_pos[0], probe_pos[1])
	machiene.down(10)
	dwn = machiene.probe_z(speed=100)[2] - 1
	for speed in prb_speeds:
		
		probe_speed = speed
		print('CURRENT SPEED: ' + str(probe_speed))
		
		for it in range(20):
		
			machiene.gotoxy(probe_pos[0], probe_pos[1])
			machiene.down(dwn)
			[x_s, y_s, z_s] = machiene.probe_z(speed=probe_speed)
			print(z_s)
			
			machiene.up()
			machiene.gotoxy(probe_pos[0] + 10, probe_pos[1] + 10)
			
			prt_str = '\t'.join([str(probe_speed), str(z_s),'\n'])
			
			data_file_o = open(data_file, 'a')
			data_file_o.write(prt_str)
			data_file_o.close()
			
	read_file(data_file)