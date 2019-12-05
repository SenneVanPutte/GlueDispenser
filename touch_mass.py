import math
import time
import matplotlib
from threading import Thread
from matplotlib import pyplot
from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation

data_file = 'probe_speed_mass.txt' 
def read_file(file_name):
	file_o = open(file_name, 'r')
	lines = file_o.readlines()
	file_o.close()
	
	data = {}
	speed_lst = []
	for line in lines:
		line_content = line.replace('\n', '').split('\t')
		speed = float(line_content[0])
		mass = float(line_content[1])
		if speed not in data:
			data[speed] = {}
			data[speed]['mass'] = []
			speed_lst.append(speed)
		data[speed]['mass'].append(mass)
	
	for spd in data:
		data[spd]['mean_mass'] = sum(data[spd]['mass'])/float(len(data[spd]['mass']))
		
		var_lst = []
		for pt in range(len(data[spd]['mass'])):
			var_lst.append((data[spd]['mass'][pt] - data[spd]['mean_mass'])**2)
		var = sum(var_lst)/float(len(var_lst))
		std = math.sqrt(var)
		
		data[spd]['std_mass'] = std
		
	speed_lst.sort()
	std_lst = []
	mean_lst = []
	for spd in speed_lst:
		std_lst.append(data[spd]['std_mass'])
		mean_lst.append(data[spd]['mean_mass'])
		
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, std_lst, label='std mass')
	ax.set(xlabel='Speed (mm/min)', ylabel='Mass std (g)', title='Mass of touchdown std')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, mean_lst, label='mean mass')
	ax.set(xlabel='Speed (mm/min)', ylabel='Mass (g)', title='Mass of touchdown')
	#ax.set_xscale('log')
	#ax.set_yscale('log')
	pyplot.show()

if __name__ == '__main__':
	machiene = gcode_handler()
	#machiene.init_code()
	scale = scale_handler()
	#scale.zero()
	#scale.calibrate()
	scale_pos = [350, 200]
	#prb_speeds = [200, 175, 150, 125, 100, 50, 25, 12, 6]
	prb_speeds = [37, 3, 1]
	#prb_speeds = [50]
	
	
	machiene.gotoxy(scale_pos[0], scale_pos[1])
	for speed in prb_speeds:
		
		probe_speed = speed
		print('')
		print('=== CURRENT SPEED: ' + str(probe_speed))
		
		for it in range(0):
			machiene.down(11)
			travel_time = 0.7 + (60./(speed + 0.))*2.4
			duration = 3.5 + travel_time
			data = []
			measure_thread = Thread(
								target=scale.read_out_time, 
								args=(duration,), 
								kwargs={
									'record': True, 
									'data': data,
									'display': False,
									}
								)
			measure_thread.setDaemon(True)
			measure_thread.start()
			
			start = time.time()
			[x_s, y_s, z_s] = machiene.probe_z(speed=probe_speed)
			end = time.time()
			
			measure_thread.join()
			
			mass_lst = []
			for point in data:
				m = point[1][0]
				mass_lst.append(m)
			mass = max(mass_lst) - min(mass_lst)
			print(mass)
			
			prt_str = '\t'.join([str(probe_speed), str(mass), '\n'])
			
			data_file_o = open(data_file, 'a')
			data_file_o.write(prt_str)
			data_file_o.close()
	read_file(data_file)
			