from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG, DRAWING_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2, calc_bend
from scale_handler import scale_handler, delay_and_flow_regulation, read_glue_type, load_f_and_p, write_f_and_p
import json
import time 

import optparse
from optparse import OptionParser

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-j', '--jig',  dest='jig',  help='Jig that needs to be loaded (for example: kapton_A, kapton_B)', type='string')
parser.add_option('-d', '--draw', dest='draw', help='Comma seperated of layer in dxf file that needs to be drawn (for example kapton or kapton,pigtail_bot)', type='string')
parser.add_option('-g', '--glue', dest='glue', help='To give in new glue mix time', action='store_true', default=False)
parser.add_option('-r', '--recon', dest='recon', help='Reconfigure LitePlacer', action='store_true', default=False)
(options, args) = parser.parse_args()

jig_key = options.jig
draw_layer = options.draw.split(',')
global_offset = [62.5, 42]

if __name__ == '__main__':
	machiene = gcode_handler()
	if options.recon:
		machiene.reconfigure()
	machiene.init_code()
	
	# Table height
	machiene.down(28) #15 for finger
	[x_s, y_s, z_s] = machiene.probe_z(speed=100)
	
	# Find kapton and kapton height
	#kapton_og = [103, 92]
	kapton_og = JIG_CFG[jig_key]['offsets']['coordinate_origin']
	machiene.gotoxy(kapton_og[0], kapton_og[1])
	machiene.down(z_s - JIG_CFG[jig_key]['offsets']['jig_hight'] -3)
	[x_t, y_t, z_t] = machiene.probe_z(speed=100)
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
	tilt_speed = 25
	needle_bend = calc_bend(tilt_speed, DRAWING_CFG[draw_layer[0]]['bend_file'])
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
			max_height=z_t-JIG_CFG[jig_key]['tilt']['max_height'],
			probe_speed=tilt_speed
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
	prev_flow_file = 'cache/prev_flow.py' 
	scale = scale_handler(options.glue)
	glue_type = read_glue_type(scale.flow_log)
	scale_pos = [350, 200]
	start_flow = time.time()
	f_c = False
	# pressure = 0
	# start_pressure = 1500
	# delay = 0.2
	answer = raw_input("Do you want to do flow calibration? (y/n) ")
	if answer == "n": 
		f_c = False
		#pressure = start_pressure
	elif answer == "y": 
		f_c = True
		#init_pressure = start_pressure
		 
		scale.zero()
		scale.calibrate()
		#scale.zero()
	else: 
		print("Unknown answer: '" + str(answer) + "', expected 'y' or 'n'")
		print("Proceeding with assumed answer 'n'")
		f_c = False
	
	#desired_flow = JIG_CFG[jig_key]['flow']['desired_flow']
	prev_desired_flow ={}
	pressure_dict = {}
	flow_dict = {}
	init_pressure = None
	for layer in draw_layer:
		
		# Check if desired flow was already measured
		do_layer = True
		for prev_layer in prev_desired_flow:
			if prev_desired_flow[prev_layer] == DRAWING_CFG[layer]['desired_flow']:
				flow_dict[layer] = flow_dict[prev_layer]
				pressure_dict[layer] = pressure_dict[prev_layer]
				do_layer = False
		if not do_layer: continue
			
		# Set initial pressure
		if init_pressure is None:
			init_pressure = DRAWING_CFG[layer]['init_pressure']
		else:
			factor_tmp = (DRAWING_CFG[layer]['desired_flow']+0.)/(measured_flow + 0.)
			factor = min(max(factor_tmp, 0.2),5)
			init_pressure = factor*DRAWING_CFG[layer]['init_pressure']
		
		# Do measurement
		if f_c: 
			mass_lim = 150
			if 'SY186' in glue_type: mass_lim = 250
			if 'WATER' in glue_type: mass_lim = 500
			print(glue_type)
			pressure, delay, measured_flow = delay_and_flow_regulation(
												machiene, 
												scale, 
												scale_pos,  
												init_pressure, 
												DRAWING_CFG[layer]['desired_flow'], 
												precision=DRAWING_CFG[layer]['flow_precision'], 
												mass_limit=mass_lim, 
												threshold=20, 
												show_data=True, 
												init=True
												)
		# Load flow and pressure
		else:
			#init_pressure = None
			#pressure = DRAWING_CFG[layer]['init_pressure']
			#measured_flow = DRAWING_CFG[layer]['desired_flow']
			measured_flow, pressure = load_f_and_p(prev_flow_file)
			
		# Set pressure and flow
		flow_dict[layer] = measured_flow
		pressure_dict[layer] = pressure
		prev_desired_flow[layer] = DRAWING_CFG[layer]['desired_flow']
		if f_c: write_f_and_p(prev_flow_file, measured_flow, pressure)
		
			
	machiene.up()
	
	#print('Drawing with delay of ' + str(delay) + ' s, and pressure of ' + str(pressure) + ' mbar')
	print("Finding flow took " + str(time.time() - start_flow) + "s")
	
	
	# machiene.gotoxy(0, 0)
	# machiene.down(28, do_tilt=False)
	# machiene.down(z_s-1, speed=100, do_tilt=False)
	# machiene.up()
	#machiene.probe_z(speed=50)
	
	# Prepare drawings
	
	start_draw = time.time()
	ref_point = machiene.tilt_map_og
	ref_h = ref_point[2] - needle_bend - JIG_CFG[jig_key]['drawing']['hight'] #- 0.85 #jig h diff, kapton thickness, actual height above
	kap_list = []
	n_sen = 1
	dx_sen = 0
	dy_sen = 0
	jig_offset = [0, 0] #(in case extra offset is needed between obj and jig)
	for ikap in range(n_sen):
		table_offset = sum_offsets(JIG_CFG[jig_key]['offsets']['drawing_position'], jig_offset)
		kap_offset = sum_offsets(table_offset, [dx_sen*ikap, dy_sen*ikap])
		print('offset: ', kap_offset) 
		kap_dict = {}
		for layer in draw_layer:
			safety_h = DRAWING_CFG[layer]['above']
			kap_dict[layer] = drawing2(
						DRAWING_CFG[layer]['file'], 
						offset=kap_offset, 
						hight=ref_h - safety_h, 
						coord_func=shift_f, 
						clean_point=[x_s, y_s, z_s-1]
						)
		kap_list.append(kap_dict)
		
	
	for kap in kap_list:
		for layer in draw_layer:
			sen = kap[layer]
			# total_line_length_mm = 2*90. + 12.
			total_line_length_mm = sen.layer_line_length(DRAWING_CFG[layer]['layer'])
			print('length ' + str(total_line_length_mm))
			total_mass_mg = DRAWING_CFG[layer]['mass']#1.25#18. #12.
			print('mass ' + str(total_mass_mg))
			#if measured_flow is None: measured_flow = 0.83 #desired_flow
			speed_mmPmin = total_line_length_mm/((total_mass_mg/flow_dict[layer])/60.)
			#speed_mmPmin = 100
			print('Calculated speed was: ' + str(speed_mmPmin) + ' mm/min')
			#sen.clear_droplet(machiene)
			delay = 0.2
			if 'SY186' in glue_type or DRAWING_CFG[layer]['is_encap']: delay = 1
			if 'PT601' in glue_type and pressure_dict[layer] < 200: delay = 0.3
			print('delay: ', delay)
			ask_r = True
			up_f = True
			if DRAWING_CFG[layer]['is_encap']: 
				ask_r = False
				up_f = False
			#if DRAWING_CFG[layer]['is_encap']: delay = 0.5
			print('Drawing '+layer+' with: '+ str(pressure_dict[layer])+ ' mbar, ' + str(flow_dict[layer])+ ' mg/s, ' + str(speed_mmPmin)+' mm/min')
			sen.draw_robust(
				machiene,
				pressure_dict[layer],
				speed_mmPmin, 
				layer=DRAWING_CFG[layer]['layer'], 
				delay=delay, 
				up_first=up_f, 
				ask_redo=ask_r,
				)
			
			# sen.draw_layer(
				# machiene,
				# pressure_dict[layer],
				# speed_mmPmin, 
				# layer=layer, 
				# delay=delay, 
				# up_first=True, 
				# )
	print("Drawing took " + str(time.time() - start_draw) + "s")

	machiene.up()
	machiene.gotoxy(scale_pos[0], scale_pos[1])
	
	