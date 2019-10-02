from glueing_cfg import JIG_OFFSET_CFG, sum_offsets
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func
from scale_handler import scale_handler, delay_and_flow_regulation


if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	
	# Table height
	machiene.down(30)
	[x_s, y_s, z_s] = machiene.probe_z(speed=25)
	
	# Find sensor ans sensor height
	#sensor_og = [103, 92]
	sensor_og = [96, 103]
	machiene.gotoxy(sensor_og[0]+2, sensor_og[1]+2)
	machiene.down(30)
	[x_t, y_t, z_t] = machiene.probe_z(speed=25)
	print([x_t, y_t, z_t])
	if z_s - z_t < 1:
		answer = raw_input("Difference was " + str(z_s - z_t) + " missed board? (y/n) ")
		if answer == "y":
			exit()
	th = z_t-2
	
	# Setup Board orientation
	#shift_f = make_quick_func(a=sensor_og[0], b=sensor_og[1])
	jig_file = 'sensor_jig_coo.py' 
	answer = raw_input("Do you want to load previous board coordinates? (y/n) ")
	if answer == "n": l_p = False
	elif answer == "y": l_p = True
	else: 
		print("Unknown answer: '" + str(answer) + "', expected 'y' or 'n'")
		print("Proceeding with assumed answer 'n'")
		l_p = False
	shift_f = make_jig_coord(
				machiene, sensor_og[0], 
				sensor_og[1], 
				dx=110, 
				dy=150, 
				up=th, 
				dth=1, 
				load_prev=l_p, 
				probe_y='y-',
				jig_file=jig_file
				)
	#f = make_quick_func( sin=0.0151768232425, cos=0.999884825386, a=65.0297324676, b=113.335272725)
	#print("took " + str(time.time() - start) + "s")
	
	# Flow Calibration
	f_c = False
	pressure = 0
	delay = 1
	answer = raw_input("Do you want to do flow calibration? (y/n) ")
	if answer == "n": f_c = False
	elif answer == "y": 
		f_c = True
		init_pressure = 100
		scale = scale_handler() 
		scale.calibrate()
		scale.zero()
	else: 
		print("Unknown answer: '" + str(answer) + "', expected 'y' or 'n'")
		print("Proceeding with assumed answer 'n'")
		f_c = False
	
	desired_flow = 30
	if f_c: pressure, delay = delay_and_flow_regulation(
								machiene, 
								scale, 
								[350, 200], 
								init_pressure, 
								desired_flow, 
								precision=(desired_flow/10 + 1), 
								duration=5, 
								threshold=40
								)
	print('Drawing with delay of ' + str(delay) + ' s, and pressure of ' + str(pressure) + ' mbar')
	
	# Prepare drawings
	sen_list = []
	n_sen = 4
	dx_sen = 0
	dy_sen = 40.25
	jig_offset = [20.5, 16.75]
	for isen in range(n_sen):
		table_offset = sum_offsets(JIG_OFFSET_CFG["sensor"], jig_offset)
		sen_offset = sum_offsets(table_offset, [dx_sen*isen, dy_sen*isen])
		print('offset: ', sen_offset) 
		sensor = drawing(
					"sensor_encap.dxf", 
					offset=sen_offset, 
					hight=th, 
					line_speed=100, 
					line_pressure=pressure, 
					coord_func=shift_f
					)
		sen_list.append(sensor)
					
	
	# Draw the sensors
	for sen in sen_list:
		sen.draw(machiene, lines=True, zigzag=False, delay=delay)
	
	