from scale_handler import scale_handler, flow_test, measure_flow
from gcode_handler import gcode_handler

import time
import matplotlib
from matplotlib import pyplot

if __name__ == '__main__':
	machiene = gcode_handler()
	#machiene.init_code()
	
	scale = scale_handler() 
	scale.conf_avg()
	scale.zero()
	#scale.calibrate()
	scale.zero()
	
	pressure = 60
	time_l = []
	flow_l = []
	delay_l = []
	for itest in range(10):
		data, delay, flow, flow_int, x_sim, y_sim, y_sim_up, y_sim_dn, redo = measure_flow(
																						machiene, 
																						scale, 
																						pressure, 
																						3,  #wait_time, 
																						150,#mass_lim, 
																						20  #mass_threshold
																						)
		flow_l.append(flow)
		delay_l.append(delay)
		time_l.append(itest)
		time.sleep(5)
	
	
	
	fig, ax = pyplot.subplots() 
	ax.plot(time_l, flow_l, 'b')
	#ax.plot(pressure_list, flow_list_up, 'r--')
	#ax.plot(pressure_list, flow_list_dn, 'r--')
	ax.set(xlabel='measurement', ylabel='flow (mg/s)', title=str(pressure)+'mbar flow consistency')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	ax.plot(time_l, delay_l, 'b')
	#ax.plot(pressure_list, flow_list_up, 'r--')
	#ax.plot(pressure_list, flow_list_dn, 'r--')
	ax.set(xlabel='measurement', ylabel='delay (s)', title=str(pressure)+'mbar delay consistency')
	pyplot.show()
	
	