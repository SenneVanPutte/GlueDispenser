import math
import matplotlib
from matplotlib import pyplot
from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation

data_file = 'sensor_hight.txt' 
def read_file(file_name):
	file_o = open(file_name, 'r')
	lines = file_o.readlines()
	file_o.close()
	
	data = {}
	speed_lst = []
	for line in lines:
		line_content = line.replace('\n', '').split('\t')
		speed = float(line_content[0])
		p0 = float(line_content[1])
		p1 = float(line_content[2])
		if speed not in data:
			data[speed] = {}
			data[speed]['p0'] = []
			data[speed]['p1'] = []
			speed_lst.append(speed)
		data[speed]['p0'].append(p0)
		data[speed]['p1'].append(p1)
	
	for spd in data:
		data[spd]['mp0'] = sum(data[spd]['p0'])/float(len(data[spd]['p0']))
		data[spd]['mp1'] = sum(data[spd]['p1'])/float(len(data[spd]['p1']))
		
		var_diff_lst = []
		var_p0_lst = []
		for pt in range(len(data[spd]['p1'])):
			var_p0_lst.append((data[spd]['p0'][pt] - data[spd]['mp0'])**2)
			var_diff_lst.append((data[spd]['p1'][pt] - data[spd]['mp1'])**2)
		var0 = sum(var_p0_lst)/float(len(var_p0_lst))
		var = sum(var_diff_lst)/float(len(var_diff_lst))
		std0 = math.sqrt(var0)
		std = math.sqrt(var)
		
		data[spd]['stdp0'] = std0
		data[spd]['stddiff'] = std
		
	speed_lst.sort()
	std0_lst = []
	std_lst = []
	mp1_lst = []
	relmp0_lst = []
	relmp1_lst = []
	for spd in speed_lst:
		std0_lst.append(data[spd]['stdp0']*1000)
		std_lst.append(data[spd]['stddiff']*1000)
		mp1_lst.append(data[spd]['mp1']*1000)
		relmp0_lst.append((data[speed_lst[0]]['mp0'] - data[spd]['mp0'])*1000)
		relmp1_lst.append((data[spd]['mp1'] - data[speed_lst[0]]['mp1'])*1000)
		
	
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, std0_lst, label='std ref point')
	ax.set(xlabel='Speed (mm/min)', ylabel=u'Hight std (\u03bcm)', title='Reference point std')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, std_lst, label='std difference')
	ax.set(xlabel='Speed (mm/min)', ylabel=u'Hight std (\u03bcm)', title='Plexi hight std')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, mp1_lst, label='p1')
	ax.legend(loc='upper right')
	ax.set(xlabel='Speed (mm/min)', ylabel=u'Hight (\u03bcm)', title='Plexi hight')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	ax.plot(speed_lst, relmp0_lst, label='p0')
	ax.set(xlabel='Speed (mm/min)', ylabel=u'Hight (\u03bcm)', title='Reference point hight')
	pyplot.show()
	

if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	#prb_speeds = [150, 125, 100, 50, 25, 12, 6]
	prb_speeds = [25, 12]
	down_h = 25
	for speed in prb_speeds:
		
		probe_speed = speed
		print('CURRENT SPEED: ' + str(probe_speed))
		
		for it in range(5):
		
			machiene.gotoxy(36, 110)
			machiene.down(down_h)
			[x_s, y_s, z_s] = machiene.probe_z(speed=probe_speed)
			print(z_s)
			
			machiene.up()
			machiene.gotoxy(46, 125)
			machiene.down(down_h)
			[x_t, y_t, z_t] = machiene.probe_z(speed=probe_speed)
			#print(z_t)
			p1 = z_s - z_t
			print('Difference: ' + str(z_s - z_t))
			
			prt_str = '\t'.join([str(probe_speed), str(z_s), str(p1),'\n'])
			
			data_file_o = open(data_file, 'a')
			data_file_o.write(prt_str)
			data_file_o.close()
			
	read_file(data_file)