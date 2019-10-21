from scale_handler import scale_handler, measure_delay, delay_and_flow_regulation
from gcode_handler import gcode_handler, drawing

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
	pressure = 200
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
								precision=2, 
								mass_limit=200, 
								threshold=20, 
								show_data=True
								)
								
	line_pos = [20, 100]
	machiene.up()
	
	test_line = drawing(
					"short_line.dxf", 
					offset=line_pos, 
					hight=0, 
					line_speed=500, 
					line_pressure=desired_press, 
					#coord_func=shift_f,
					#clean_point=[0, y_s, z_s-1]
					)
	test_line.draw(machiene, lines=True, zigzag=False, delay=delay_t)
	
	#machiene.gotoxy(line_pos[0], line_pos[1])
	#machiene.set_pressure(desired_press)
	#machiene.gotoxy(line_pos[0], line_pos[1]+10)
	#machiene.stop_pressure()
	
	
	
								
	print('Desired pressure is '+str(desired_press) + ' mbar, delay is ' + str(delay_t) + ' s' )
	
	