from glueing_cfg import JIG_OFFSET_CFG
from gcode_handler import gcode_handler, drawing
import math
import time
import json
import random


def probe(machiene, start_x, start_y, dir='y+', threshold_h=19, step=1, speed=50, up=15):
	if step < 0.025:
		print("finished")
		return
	if dir[0] == 'y': 
		pos_idx = 1
		if dir[1] == '+':
			d_pos = [0, step]
		elif dir[1] == '-':
			d_pos = [0, -step]
		else: raise ValueError("Unknown probe direction '" + str(dir[1]) + "' should be '+' or '-'" )
	elif dir[0] == 'x': 
		pos_idx = 0
		if dir[1] == '+':
			d_pos = [step, 0]
		elif dir[1] == '-':
			d_pos = [-step, 0]
		else: raise ValueError("Unknown probe direction '" + str(dir[1]) + "' should be '+' or '-'" )
	else: raise ValueError("Unknown probe axis '" + str(dir[0]) + "' should be 'x' or 'y'")
	#machiene.up()
	machiene.gotoxy(start_x, start_y, speed=speed)
	machiene.down(up)
	pos = machiene.probe_z(speed=25, up=up, max_z = threshold_h + 1)
	#print(pos)
	start_z = pos[2]
	new_z = pos[2]
	prev_z = pos[2]
	it = 1
	final_x = start_x
	final_y = start_y
	while new_z < threshold_h:
		prev_z = new_z
		final_x = start_x + it*d_pos[0]
		final_y = start_y + it*d_pos[1]
		machiene.gotoxy(final_x, final_y, speed=speed)
		posy = machiene.probe_z(speed=10, up = new_z - 0.75, max_z = threshold_h + 1)
		#print(posy)
		new_z = posy[2]
		it += 1
	if final_x == start_x and final_y == start_y:
		#print("move back")
		return probe(machiene, final_x - d_pos[0], final_y - d_pos[1], dir=dir, threshold_h=threshold_h, step=step, speed=speed, up=up)
	elif step < 0.1:
		print("edge found at " + str([final_x, final_y]))
		return [final_x, final_y]
	else:
		#print("next")
		return probe(machiene, final_x - d_pos[0], final_y - d_pos[1], dir=dir, threshold_h=threshold_h, step=(step + 0.0)/4., speed=max((speed + 0.0)/2., 25), up=prev_z - 0.75)
	
def make_jig_coord(machiene, x_guess, y_guess, up=15, dx=135, dy=100, dth=1.15, load_prev=False):
	data_fn = "prev_board_coo.py"
	old_f = open(data_fn, "r")
	try:
		old_data = json.load(old_f)
	except:
		old_data = None
	old_f.close()
	if not load_prev:
		machiene.gotoxy(x_guess, y_guess)
		machiene.down(up)
		th_h = machiene.probe_z(speed=25)[2] + dth
		[x1, y1] = probe(machiene, x_guess, y_guess, threshold_h=th_h, up=th_h - 0.5 - dth)
		machiene.up()
		machiene.gotoxy(x_guess + dx, y_guess)
		machiene.down(up - 4)
		th_h = machiene.probe_z(speed=25)[2] + dth
		[x2, y2] = probe(machiene, x_guess + dx, y_guess, threshold_h=th_h, up=th_h - 0.5 - dth, step=4, speed=100)
		machiene.up()
		machiene.gotoxy(x_guess, y_guess + dy)
		machiene.down(up - 6)
		th_h = machiene.probe_z(speed=25)[2] + dth
		[x3, y3] = probe(machiene, x_guess, y_guess + dy, dir='x-', threshold_h=th_h + 1, step=4, speed=100, up=th_h - 0.5 - dth)
		machiene.up()
	
		sin_th = (y2 - y1 + 0.)/(math.sqrt((x2 - x1 + 0.)**2 + (y2 - y1 + 0.)**2))
		cos_th = (x2 - x1 + 0.)/(math.sqrt((x2 - x1 + 0.)**2 + (y2 - y1 + 0.)**2))
	
	
		print("sin = " + str(sin_th) + ",\t theta = " + str(math.asin(sin_th)) + " (" + str(math.asin(sin_th)*180/math.pi) + ")")
		print("cos = " + str(cos_th) + ",\t theta = " + str(math.acos(cos_th)) + " (" + str(math.acos(cos_th)*180/math.pi) + ")")
	
		if x1 == x2:
			raise ValueError("make_jig_coord: first point and second point can not have the same x value")
		if y2 == y1:
			print("Congratz, perfectly parallel")
			b = y1
			a = x3
		else:
			tan_th = (y2 - y1 + 0.)/(x2 - x1 + 0.)
			a = ((x3 + 0.)/tan_th + y3 - y1 + tan_th*x1)/(tan_th + 1/tan_th)
			b = tan_th*(a - x1) + y1
	
		print("a = " + str(a))
		print("b = " + str(b))
	
		board_coo = make_quick_func( sin=sin_th, cos=cos_th, a=a, b=b)
		
		board_coo_f = open(data_fn, "w")
		
		data = {
			"sin": sin_th,
			"cos": cos_th,
			"offset_x": a,
			"offset_y": b,
		}
		
		board_coo_f.write(json.dumps(data))
		board_coo_f.close()
		return board_coo
	else:
		if old_data is None: raise ValueError("No previous board data found ( " + data_fn + " empty?)")
		board_coo = make_quick_func( sin=old_data["sin"], cos=old_data["cos"], a=old_data["offset_x"], b=old_data["offset_y"])
		return board_coo
	
def make_quick_func( sin=0, cos=1, a=80, b=110):
	def board_coo(x=None, y=None, pos=None):
		if pos is None and (x is None or y is None): raise ValueError("x, y and pos can't both be None")
		if pos is None:
			x_temp = x
			y_temp = y
		else:
			x_temp = pos[0]
			y_temp = pos[1]
		x_m = a + (cos*x_temp - sin*y_temp)
		y_m = b + (cos*y_temp + sin*x_temp)
		return [x_m, y_m]
	return board_coo

	
if __name__ == "__main__":
	machiene = gcode_handler()
	machiene.init_code()
	rand_off = [0,0]#[random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)]
	
	start = time.time()
	
	# Table height
	machiene.down(30)
	[x_s, y_s, z_s] = machiene.probe_z(speed=25)
	
	# Look if Board is there, setup threshold
	machiene.gotoxy(80+rand_off[0], 110+rand_off[1])
	machiene.down(10)
	[x_t, y_t, z_t] = machiene.probe_z(speed=25)
	print([x_t, y_t, z_t])
	if z_s - z_t < 14:
		answer = raw_input("Difference was " + str(z_s - z_t) + " missed board? (y/n) ")
		if answer == "y":
			exit()
	th = z_t-2
	#print("threshold_h = " + str(th))
	
	# Setup Board orientation
	answer = raw_input("Do you want to load previous board coordinates? (y/n) ")
	if answer == "n": l_p = False
	elif answer == "y": l_p = True
	else: 
		print("Unknown answer: '" + str(answer) + "', expected 'y' or 'n'")
		print("Proceeding with assumed answer 'n'")
		l_p = False
	f = make_jig_coord(machiene, 80+rand_off[0], 110+rand_off[1], up=th, load_prev=l_p)
	#f = make_quick_func( sin=0.0151768232425, cos=0.999884825386, a=65.0297324676, b=113.335272725)
	print("took " + str(time.time() - start) + "s")
	
	# Setup Board tilt
	data_fn = "prev_board_coo.py"
	old_f = open(data_fn, "r")
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
		machiene.measure_tilt_3p(f(pos=[10, -5]), f(pos=[150, -5]), f(pos=[10, 120]), max_height=z_t-6)
		old_data["tilt_map"] = machiene.tilt_map
		old_data["tilt_map_og"] = machiene.tilt_map_og
	else:
		machiene.tilt_map = old_data["tilt_map"]
		machiene.tilt_map_og = old_data["tilt_map_og"]
	old_f = open(data_fn, "w")
	old_f.write(json.dumps(old_data))
	old_f.close()
	
	#machiene.gotoxy(position=f(pos=[37, 16]))
	#machiene.down(12)
	#ref_point = machiene.probe_z(speed=10)
	#machiene.tilt_map_og = ref_point
	#print(ref_point)
	ref_point = machiene.tilt_map_og
	#ref_h = ref_point[2] - 0.125
	ref_h = ref_point[2] - 5.3 - 0.2 - 0.85
	
	# Deposit the glue 
	#board = drawing("board_m_og.dxf", offset=BOARD_CFG["jig_offset"], hight=posy[2]-0.25, line_speed=500, line_pressure=52, coord_func=f)
	board = drawing(
					"board_m_og.dxf", 
					offset=JIG_OFFSET_CFG["kapton"], 
					hight=ref_h, 
					line_speed=100, 
					line_pressure=400, 
					coord_func=f, 
					clean_point=[x_s, y_s, z_s-1]
					)
	print("____draw____")
	board.draw(machiene, lines=True, zigzag=False, delay=1)
	
	