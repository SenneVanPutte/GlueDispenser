import time
import copy
from glueing_cfg import MIN_OFFSET, TABLE_HEIGHT
from gcode_handler import gcode_handler, drawing

speed_dict = {
	5 : 2000,
	50: 1600,
	100: 1200,
	158: 800,
	200: 400,
}

pressure_dict = {
	1: 100,
	2: 200,
	3: 300,
	4: 400,
	5: 500,
} 


def drip_test(machiene, x=MIN_OFFSET[0] , y=MIN_OFFSET[1]):
	machiene.up()
	machiene.gotoxy( x, y)
	print("Start drip test")
	#answer = raw_input("Initial pressure guess? (between 1000 and 0 in mbar)")
	#try:
	#	print("Guessed pressure: " + str(int(answer)) + " mbar")
	#	press_guess = int(answer)
	#except:
	#	print("No guessed pressure found, go to 100 mbar by default")
	#	press_guess = 1500
	time.sleep(3)
	not_satisfied = True
	prev_pressure = 0
	pressure = 50
	drip_time = 5
	is_dripping = False
	while not_satisfied:
		if prev_pressure >= 5500 and pressure >= 5500:
			print("Switch to bigger nozzle")
			raw_input("Press ENETR when nozzle switched")
			pressure = 50
			prev_pressure = 0
			continue
		if prev_pressure <= 0 and pressure <= 0:
			print("Switch to smaller nozzle")
			raw_input("Press ENETR when nozzle switched")
			pressure = 50
			prev_pressure = 0
			continue
		print("Get ready to count drops!!")
		time.sleep(2)
		drip(machiene, pressure=pressure, drip_time=drip_time)
		if not is_dripping:
			answer = raw_input("Was the liquid dripping out? (y/n) ")
			if answer == "n": 
				print("Switch to bigger nozzle")
				raw_input("Press ENETR when nozzle switched")
				continue
			elif answer == "y":
				#pressure = press_guess
				is_dripping = True
				#continue
		if is_dripping:
			answer = raw_input("Did more then 3 drops come out? (y/n) ")
			if answer == "n":
				if prev_pressure < pressure:
					new_press = min(5500, pressure + abs(pressure - prev_pressure))
				else:
					new_press = min(5500, pressure + round(abs(prev_pressure - pressure)/2))
				prev_pressure = pressure
				pressure = new_press
				continue
			elif answer == "y":
				answer = raw_input("Did more then 15 drops come out? (y/n) ")
				if answer == "n":
					not_satisfied = False
					print("flow pressure = " + str(pressure) + ", change scale = " + str(abs(pressure - prev_pressure)))
					return pressure, abs(pressure - prev_pressure)
				elif answer == "y":
					pressure = pressure
					if prev_pressure < pressure:
						new_press = max(0, pressure - round(abs(pressure - prev_pressure)/2))
					else:
						new_press = max(0, pressure - abs(prev_pressure - pressure))
					prev_pressure = pressure
					pressure = new_press
					continue
	
def drip(machiene, pressure=100, drip_time=10):
	machiene.set_pressure(pressure, no_flush=False)
	machiene.wait(drip_time, sleep=True)
	machiene.stop_pressure()

def line_test(machiene, init_pressure, x1=MIN_OFFSET[0]+50, y1=MIN_OFFSET[1], x2=MIN_OFFSET[0]+50, y2=MIN_OFFSET[1]+100):
	machiene.gotoxy(x1, y1)
	
	print("Start line test")
	machiene.down(TABLE_HEIGHT)
	raw_input("set pen")
	machiene.up()
	answer = raw_input("Initial speed guess? (between 2000 and 0 in mm/min) ")
	try:
		print("Guessed speed: " + str(int(answer)) + " mm/min")
		speed = int(answer)
	except:
		print("No guessed speed found, go to 2000 mm/min by default")
		speed = 2000
	time.sleep(3)
	not_satisfied = True
	pressure = init_pressure
	#speed = 2000
	is_line = False
	while not_satisfied:
		
		raw_input("time to clean")
		line(machiene, pressure, speed=speed, x1=x1, y1=y1, x2=x2, y2=y2)
		if not is_line:
			answer = raw_input("Was there a line? (y/n) ")
			if answer == "n": 
				speed -= 400
				continue
			elif answer == "y":
				is_line = True
				is_dripping = True
		if is_line:
			answer = raw_input("Was the line too thick? (y/n) ")
			if answer == "n":
				answer = raw_input("Was the line too slim? (y/n) ")
				if answer == "n":
					not_satisfied = False
					print("move speed = " + str(speed))
					return speed
				if answer == "y":
					speed -= 200
					continue
			elif answer == "y":
				speed += 200
				continue
				print("flow pressure = " + str(pressure))
				return pressure
	
def line_test2(machiene, init_pressure, pressure_scale, x1=MIN_OFFSET[0]+50, y1=MIN_OFFSET[1], x2=MIN_OFFSET[0]+50, y2=MIN_OFFSET[1]+100):
	machiene.gotoxy(x1, y1)
	
	print("Start line test")
	machiene.down(TABLE_HEIGHT)
	raw_input("set pen")
	machiene.up()
	machiene.gotoxy(position=AWAY)
	not_satisfied = True
	pressure = init_pressure
	max_pressure = min(5500, init_pressure + pressure_scale)
	min_pressure = max(0, init_pressure - pressure_scale)
	max_speed = 2000
	min_speed = 200
	prev_speed = min_speed
	speed = 1100
	is_line = False
	while not_satisfied:
		
		raw_input("Time to clean, and put plexi glass in place!")
		print("testing speed " + str(speed) + " and pressure " + str(pressure)) 
		line(machiene, pressure, speed=speed, x1=x1, y1=y1, x2=x2, y2=y2)
		machiene.gotoxy(position=AWAY)
		print("Take out plexi glass and test the line thickness!")
		answer = raw_input("Was the line too thick? (y/n) ")
		if answer == "n":
			answer = raw_input("Was the line too slim? (y/n) ")
			if answer == "n":
				not_satisfied = False
				print("move speed = " + str(speed))
				print("glue pressure = " + str(pressure))
				return speed, pressure
			if answer == "y":
				if prev_speed > speed:
					new_speed = max(min_speed, speed - abs(speed - prev_speed))
				else:
					new_speed = max(min_speed, speed - round(abs(speed - prev_speed)/2))
				prev_speed = speed
				speed = new_speed
				#continue
		elif answer == "y":
			if prev_speed < speed:
				new_speed = min(max_speed, speed + abs(speed - prev_speed))
			else:
				new_speed = min(max_speed, speed + round(abs(speed - prev_speed)/2))
			prev_speed = speed
			speed = new_speed
			#continue
		print(" speed adapted")
		if prev_speed >= max_speed or prev_speed <= min_speed:
			print(" adapting pressure")
			if prev_speed <= min_speed:
				new_pressure = pressure + round(press_scale/4)
			else:
				new_pressure = pressure - round(press_scale/4)
			print(" old pressure = " + str(pressure) + ", new pressure = " + str(new_pressure))
			pressure = new_pressure
			speed = 1100
			prev_speed = 200

def line_test_multi(machiene, init_pressure, pressure_scale):
	pressure = init_pressure
	speed_dict_ad = copy.deepcopy(speed_dict)
	press_dict_ad = copy.deepcopy(pressure_dict)
	max_speed = 1000
	min_speed = 200
	t_speed = max_speed
	b_speed = min_speed
	spd_keys = []
	for key in speed_dict:
		spd_keys.append(key)
	spd_keys.sort()
	all_thick=True
	all_thin=True
	
	not_satisfied = True
	
	
	
	while not_satisfied:
		print("Glue pressure: " + str(pressure) + " mbar")
		for i,key in enumerate(spd_keys):
			speed_dict_ad[key] = b_speed + i*round((t_speed - b_speed)/4)
			print("Line " + str(i+1) + " has speed " + str(speed_dict_ad[spd_keys[i]]) + " mm/min")
		for i in range(1,6):
			press_dict_ad[i] = pressure
		 
		test = drawing("line_thickness2_og.dxf", hight=TABLE_HEIGHT, speed_dict=speed_dict_ad, pressure_dict=press_dict_ad)
		raw_input("Time to clean, and put plexi glass in place!")
		test.draw(machiene, zigzag=False)
		machiene.gotoxy(position=AWAY)
		if all_thick:
			answer = raw_input("Where all lines to thick? (y/n) ")
			if answer == "y":
				print("Turning down pressure")
				pressure -= round(pressure_scale/4)
				continue
			elif answer == "n":
				all_thick = False
		if all_thin:
			answer = raw_input("Where all lines to slim? (y/n) ")
			if answer == "y":
				print("Turning up pressure")
				pressure += round(pressure_scale/4)
				continue
			elif answer == "n":
				all_thin = False
		if not all_thin and not all_thick:
			answer = raw_input("Was there a perfect line? (y/n) ")
			if answer == "n":
				low = raw_input("Give highest thick line (lower line boundary): (1-5) ")
				hig = raw_input("Give lowest thin line   (higher line boundary): (1-5) ")
				n_low = int(low)
				n_hig = int(hig)
				new_b_speed = speed_dict_ad[spd_keys[n_low-1]]
				new_t_speed = speed_dict_ad[spd_keys[n_hig-1]]
				if n_hig == 5:
					new_t_speed += round(abs(t_speed - b_speed)/4)
				if n_low == 1:
					new_b_speed -= round(abs(t_speed - b_speed)/4)
				if new_b_speed < min_speed:
					print("Turning up pressure slightly")
					pressure += round(pressure_scale/8)
					new_b_speed = min_speed
				t_speed = new_t_speed
				b_speed = new_b_speed
				continue
			elif answer == "y":
				answer = raw_input('Select this "perfect line": (1-5) ')
				n_perfect = int(answer)
				perf_press = pressure
				perf_speed = speed_dict_ad[spd_keys[n_perfect-1]]
				not_satisfied = False
				print("move speed = " + str(perf_speed))
				print("glue pressure = " + str(perf_press))
				return perf_speed, perf_press
		print("Should never be reached!!!!!!!!!!!!!")
			
	
		
			
def line(machiene, pressure, speed=2000, x1=MIN_OFFSET[0], y1=MIN_OFFSET[1], x2=MIN_OFFSET[0], y2=(MIN_OFFSET[1]+100), height=TABLE_HEIGHT, set_pen=False ):
	machiene.gotoxy(x1, y1)
	machiene.down(height)
	if set_pen:
		raw_input("set pen")
	machiene.set_pressure(pressure)
	machiene.gotoxy(x2, y2, speed=speed)
	machiene.stop_pressure()
	machiene.up()
	


AWAY = [100, 250]



	
if __name__ == "__main__":
	machiene = gcode_handler()
	machiene.init_code()
	press, press_scale = drip_test(machiene)
	machiene.gotoxy(position=AWAY)
	raw_input("Clean up after drip test")
	#speed, pressure = line_test2(machiene, press, press_scale)
	speed, pressure = line_test_multi(machiene, press, press_scale)
	#speed = line_test(machiene, press)
	#test = drawing("glue_og.dxf", line_speed=3, line_pressure=3)
	#test = drawing("Line_Thickness_og.dxf", speed_dict=speed_dict, pressure_dict=pressure_dict)
	#test.draw(machiene)