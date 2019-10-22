from scale_handler import scale_handler, measure_delay, delay_and_flow_regulation
from gcode_handler import gcode_handler

import matplotlib
from matplotlib import pyplot

if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	
	scale = scale_handler() 
	#scale.conf_avg("b")
	#scale.calibrate()
	scale.zero()
	
	# pressure = 100
	# desired_flow = 10
	
	# Water
	pressure = 100
	desired_flow = 5
	#scale_pos = [0, 0, 0]
	scale_pos = [350, 200, 0]
	
	#delay, delay_up, delay_dn, press_guess, data = measure_delay(machiene, scale, [0, 0, 0], pressure, duration=3, threshold=30, desired_flow=desired_flow)
	#print('Delay is ' + str(delay) + ', uncert window: [' + str(delay_dn) + ', ' + str(delay_up)  + ']'  ) 
	#scale.plot_data(data)
	
	#raw_input('Starting flow reg')
	#init_pressure = pressure
	#if press_guess is not None: init_pressure = press_guess

	desired_press, delay_t, flow = delay_and_flow_regulation(
								machiene, 
								scale, 
								scale_pos, 
								pressure, 
								desired_flow, 
								precision=1, 
								mass_limit=150, 
								threshold=20, 
								show_data=True
								)
								
	print('Desired pressure is '+str(desired_press) + ' mbar, delay is ' + str(delay_t) + ' s' )
	