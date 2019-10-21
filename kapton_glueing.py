from glueing_cfg import JIG_OFFSET_CFG, sum_offsets
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func
from scale_handler import scale_handler, delay_and_flow_regulation
import json
import time 


if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	
	# Table height
	machiene.down(28)
	[x_s, y_s, z_s] = machiene.probe_z(speed=50)
	
	# Find kapton and kapton height
	#kapton_og = [103, 92]
	kapton_og = [80, 110]
	machiene.gotoxy(kapton_og[0], kapton_og[1])
	machiene.down(15)
	[x_t, y_t, z_t] = machiene.probe_z(speed=25)
	print([x_t, y_t, z_t])
	if z_s - z_t < 13:
		answer = raw_input("Difference was " + str(z_s - z_t) + " missed board? (y/n) ")
		if answer == "y":
			exit()
	th = z_t-2
	
	# Setup Board orientation
	#shift_f = make_quick_func(a=kapton_og[0], b=kapton_og[1])
	start_coo = time.time()
	jig_file = 'kapton_jig_coo.py' 
	answer = raw_input("Do you want to load previous board coordinates? (y/n) ")
	if answer == "n": l_p = False
	elif answer == "y": l_p = True
	else: 
		print("Unknown answer: '" + str(answer) + "', expected 'y' or 'n'")
		print("Proceeding with assumed answer 'n'")
		l_p = False
	shift_f = make_jig_coord(
				machiene, 
				kapton_og[0], 
				kapton_og[1], 
				dx=135, 
				dy=100, 
				up=th, 
				dth=1, 
				load_prev=l_p, 
				jig_file=jig_file
				)
	#f = make_quick_func( sin=0.0151768232425, cos=0.999884825386, a=65.0297324676, b=113.335272725)
	print("Making board coordinates took " + str(time.time() - start_coo) + "s")
	
	# Setup Board tilt
	start_tilt = time.time()
	old_f = open(jig_file, "r")
	try:
		old_data = json.load(old_f)
	except:
		old_data = None
	old_f.close()
	answer = raw_input("Do you want to load previous board tilt? (y/n) ")
	if answer == "n": l_p = False
	elif answer == "y": l_p = True
	else: 
		print("Unknown answer: '" + str(answer) + "', expected 'y' or 'n'")
		print("Proceeding with assumed answer 'n'")
		l_p = False
	if not l_p:
		machiene.measure_tilt_3p(
			shift_f(pos=[10, -5]), 
			shift_f(pos=[150, -5]), 
			shift_f(pos=[10, 120]), 
			max_height=z_t-6
			)
		
		old_data["tilt_map"] = machiene.tilt_map
		old_data["tilt_map_og"] = machiene.tilt_map_og
	else:
		machiene.tilt_map = old_data["tilt_map"]
		machiene.tilt_map_og = old_data["tilt_map_og"]
	old_f = open(jig_file, "w")
	old_f.write(json.dumps(old_data))
	old_f.close()
	print("Making board tilt took " + str(time.time() - start_tilt) + "s")
	
	# Flow Calibration
	scale_pos = [350, 200]
	start_flow = time.time()
	f_c = False
	pressure = 0
	start_pressure = 200
	delay = 0.1
	answer = raw_input("Do you want to do flow calibration? (y/n) ")
	if answer == "n": 
		f_c = False
		pressure = start_pressure
	elif answer == "y": 
		f_c = True
		init_pressure = start_pressure
		scale = scale_handler() 
		scale.calibrate()
		scale.zero()
	else: 
		print("Unknown answer: '" + str(answer) + "', expected 'y' or 'n'")
		print("Proceeding with assumed answer 'n'")
		f_c = False
	
	desired_flow = 10
	measured_flow = None
	if f_c: 
		pressure, delay, measured_flow = delay_and_flow_regulation(
												machiene, 
												scale, 
												scale_pos,  
												init_pressure, 
												desired_flow, 
												precision=5, 
												mass_limit=150, 
												threshold=20, 
												show_data=True, 
												init=True
												)
		machiene.up()
	
	print('Drawing with delay of ' + str(delay) + ' s, and pressure of ' + str(pressure) + ' mbar')
	print("Finding flow took " + str(time.time() - start_flow) + "s")
	
	# Prepare drawings
	total_line_length_mm = 2*90. + 12.
	total_mass_mg = 20.
	if measured_flow is None: measured_flow = desired_flow
	speed_mmPmin = total_line_length_mm/((total_mass_mg/measured_flow)/60.)
	print('Calculated speed was: ' + str(speed_mmPmin) + ' mm/min')
	start_draw = time.time()
	ref_point = machiene.tilt_map_og
	ref_h = ref_point[2] - 5.3 - 0.2 #- 0.85 #jig h diff, kapton thickness, actual height above
	kap_list = []
	n_sen = 1
	dx_sen = 0
	dy_sen = 0
	jig_offset = [0, 0] #(in case extra offset is needed between obj and jig)
	for ikap in range(n_sen):
		table_offset = sum_offsets(JIG_OFFSET_CFG["kapton"], jig_offset)
		kap_offset = sum_offsets(table_offset, [dx_sen*ikap, dy_sen*ikap])
		print('offset: ', kap_offset) 
		kapton = drawing(
					"board_m_og.dxf", 
					offset=kap_offset, 
					hight=ref_h, 
					line_speed=speed_mmPmin, 
					line_pressure=pressure, 
					coord_func=shift_f,
					clean_point=[x_s, y_s, z_s-1]
					)
		kap_list.append(kapton)
					
	
	# Draw the kaptons
	#machiene.gotoxy(ref_point[0], ref_point[1])
	#machiene.probe_z()
	#time.sleep(1)
	for sen in kap_list:
		sen.draw(machiene, lines=True, zigzag=False, delay=delay)
	print("Drawing took " + str(time.time() - start_draw) + "s")

	machiene.up()
	machiene.gotoxy(scale_pos[0], scale_pos[1])
	
	