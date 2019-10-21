from scale_handler import scale_handler, flow_test#, flow_test2
from gcode_handler import gcode_handler

import matplotlib
from matplotlib import pyplot

if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	
	scale = scale_handler() 
	scale.conf_avg()
	scale.zero()
	#scale.calibrate()
	#scale.zero()
	#pressure_list=range(750,1000,25)
	#pressure_list = [100, 200, 300, 400, 500, 750, 1000, 1500, 2000]
	#pressure_list = [50, 75, 100, 125, 150, 200, 250, 300, 350, 400, 500, 750]
	#pressure_list = [50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160]
	pressure_list = [4000]
	#flow_list = flow_test(machiene, scale, [180, 140, 0], pressure_list, duration=5)
	#machiene.down(8)
	#flow_list, flow_list_up, flow_list_dn, delay_list = flow_test(machiene, scale, [0, 0, 0], pressure_list, duration=7, empty_check=False)
	scale_pos = [0, 0, 0]
	#scale_pos = [350, 200, 0]
	flow_list, flow_list_up, flow_list_dn, delay_list = flow_test(machiene, scale, scale_pos, pressure_list, mass_lim=200, empty_check=False)
	
	fig, ax = pyplot.subplots() 
	ax.plot(pressure_list, flow_list, 'b')
	ax.plot(pressure_list, flow_list_up, 'r--')
	ax.plot(pressure_list, flow_list_dn, 'r--')
	ax.set(xlabel='pressure (mbar)', ylabel='flow (mg/s)', title='Flow vs Pressure')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	ax.plot(pressure_list, delay_list, 'b')
	#ax.plot(pressure_list, flow_list_up, 'r--')
	#ax.plot(pressure_list, flow_list_dn, 'r--')
	ax.set(xlabel='pressure (mbar)', ylabel='delay (s)', title='Delay vs Pressure')
	pyplot.show()
	
	