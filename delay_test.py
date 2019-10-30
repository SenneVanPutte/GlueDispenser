from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation
import json
import time 

import optparse
from optparse import OptionParser

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-j', '--jig',  dest='jig',  help='Jig that needs to be loaded (for example: kapton_A, kapton_B)', type='string')
parser.add_option('-d', '--draw', dest='draw', help='Comma seperated of layer in dxf file that needs to be drawn (for example kapton or kapton,pigtail_bot)', type='string')
(options, args) = parser.parse_args()

jig_key = options.jig
draw_layer = options.draw.split(',')

if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	
	# Table height
	machiene.down(28)
	[x_s, y_s, z_s] = machiene.probe_z(speed=50)
	
	# Find kapton and kapton height
	#kapton_og = [103, 92]
	kapton_og = JIG_CFG[jig_key]['offsets']['table_position']
	machiene.gotoxy(kapton_og[0], kapton_og[1])
	machiene.down(z_s - JIG_CFG[jig_key]['offsets']['jig_hight'] -3)
	[x_t, y_t, z_t] = machiene.probe_z(speed=25)
	print([x_t, y_t, z_t])
	if z_s - z_t < JIG_CFG[jig_key]['offsets']['jig_hight'] - 2:
		answer = raw_input("Difference was " + str(z_s - z_t) + " missed board? (y/n) ")
		if answer == "y":
			exit()
	th = z_t-2
	
	# Setup Board orientation
	#shift_f = make_quick_func(a=kapton_og[0], b=kapton_og[1])
	start_coo = time.time()
	jig_file = JIG_CFG[jig_key]['probe']['jig_file']
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
				dx=JIG_CFG[jig_key]['probe']['dx'], 
				dy=JIG_CFG[jig_key]['probe']['dy'], 
				probe_x=JIG_CFG[jig_key]['probe']['probe_x'],
				probe_y=JIG_CFG[jig_key]['probe']['probe_y'],
				up=th, 
				dth=JIG_CFG[jig_key]['probe']['dth'], 
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
			shift_f(pos=JIG_CFG[jig_key]['tilt']['p1']), 
			shift_f(pos=JIG_CFG[jig_key]['tilt']['p2']), 
			shift_f(pos=JIG_CFG[jig_key]['tilt']['p3']), 
			max_height=z_t-JIG_CFG[jig_key]['tilt']['max_height']
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
	start_pressure = 1000
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
	
	#desired_flow = JIG_CFG[jig_key]['flow']['desired_flow']
	desired_flow = 3
	measured_flow = None
	if f_c: 
		pressure, delay, measured_flow = delay_and_flow_regulation(
												machiene, 
												scale, 
												scale_pos,  
												init_pressure, 
												desired_flow, 
												precision=0.5, 
												mass_limit=150, 
												threshold=20, 
												show_data=True, 
												init=True
												)
		machiene.up()
	
	print('Drawing with delay of ' + str(delay) + ' s, and pressure of ' + str(pressure) + ' mbar')
	print("Finding flow took " + str(time.time() - start_flow) + "s")
	
	
	# machiene.gotoxy(0, 0)
	# machiene.down(28, do_tilt=False)
	# machiene.down(z_s-1, speed=100, do_tilt=False)
	# machiene.up()
	#machiene.probe_z(speed=50)
	
	# Prepare drawings
	total_line_length_mm = 2*90. + 12.
	total_mass_mg = 12.
	if measured_flow is None: measured_flow = 0.528
	speed_mmPmin = total_line_length_mm/((total_mass_mg/measured_flow)/60.)
	#speed_mmPmin = 100
	print('Calculated speed was: ' + str(speed_mmPmin) + ' mm/min')
	start_draw = time.time()
	ref_point = machiene.tilt_map_og
	ref_h = ref_point[2] - JIG_CFG[jig_key]['drawing']['hight'] #- 0.85 #jig h diff, kapton thickness, actual height above
	kap_list = []
	n_sen = 7
	dx_sen = 10
	dy_sen = 0
	jig_offset = [0, 0] #(in case extra offset is needed between obj and jig)
	for ikap in range(n_sen):
		table_offset = sum_offsets(JIG_CFG[jig_key]['offsets']['coordinate_origin'], jig_offset)
		kap_offset = sum_offsets(table_offset, [dx_sen*ikap, dy_sen*ikap])
		print('offset: ', kap_offset) 
		# kapton = drawing(
					# JIG_CFG[jig_key]['drawing']['file'], 
					# offset=kap_offset, 
					# hight=ref_h, 
					# line_speed=speed_mmPmin, 
					# line_pressure=pressure, 
					# coord_func=shift_f,
					# clean_point=[x_s, y_s, z_s-1]
					# )
		kapton = drawing2(
					JIG_CFG[jig_key]['drawing']['file'], 
					offset=kap_offset, 
					hight=ref_h, 
					coord_func=shift_f, 
					clean_point=[x_s, y_s, z_s-1]
					)
		kap_list.append(kapton)
					
	
	# Draw the kaptons
	#machiene.gotoxy(ref_point[0], ref_point[1])
	#machiene.probe_z()
	#time.sleep(1)
	first_l = [[10, 10],[10, 60]]
	delay_t = 0.125
	for sen in kap_list:
		#sen.draw(machiene, lines=True, zigzag=False, delay=delay)
		#sen.draw_lines(
		#		machiene, 
		#		pressure, 
		#		speed_mmPmin, 
		#		layer='glue_lines', 
		#		delay=delay, 
		#		up_first=True, 
		#		)
		delay_t += 0.025
		print("Delay put in: " + str(delay_t))
		for layer in draw_layer:
			# sen.draw_lines(
				# machiene, 
				# pressure, 
				# speed_mmPmin, 
				# layer=layer, 
				# delay=0.2, 
				# up_first=True, 
				# )
			sen.clear_droplet(machiene)
			sen.draw_lines(
				machiene, 
				pressure, 
				speed_mmPmin, 
				#layer=layer, 
				delay=delay_t, 
				up_first=True, 
				rel_pos_start=first_l[0], 
				rel_pos_end=first_l[1]
				)
			
	print("Drawing took " + str(time.time() - start_draw) + "s")

	machiene.up()
	machiene.gotoxy(scale_pos[0], scale_pos[1])
	
	