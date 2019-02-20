import time
from glueing_cfg import MIN_OFFSET
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
	pressure = 1500
	drip_time = 5
	is_dripping = False
	while not_satisfied:
		if prev_pressure >= 5500 and pressure >= 5500:
			print("Switch to bigger nozzle")
			raw_input("Press ENETR when nozzle switched")
			pressure = 1500
			prev_pressure = 0
			continue
		if prev_pressure <= 0 and pressure <= 0:
			print("Switch to smaller nozzle")
			raw_input("Press ENETR when nozzle switched")
			pressure = 1500
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
	machiene.down()
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
	machiene.down()
	raw_input("set pen")
	machiene.up()
	not_satisfied = True
	pressure = init_pressure
	max_pressure = min(5500, init_pressure + pressure_scale)
	min_pressure = max(0, init_pressure - pressure_scale)
	max_speed = 1000
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
				
def line(machiene, pressure, speed=2000, x1=MIN_OFFSET[0], y1=MIN_OFFSET[1], x2=MIN_OFFSET[0], y2=(MIN_OFFSET[1]+100)):
	machiene.gotoxy(x1, y1)
	machiene.down()
	machiene.set_pressure(pressure)
	machiene.gotoxy(x2, y2, speed=speed)
	machiene.stop_pressure()
	machiene.up()
	


AWAY = [100, 250]


	
if __name__ == "__main__":
	machiene = gcode_handler()
	#machiene.init_code()
	press, press_scale = drip_test(machiene)
	machiene.gotoxy(position=AWAY)
	raw_input("Clean up after drip test")
	speed, pressure = line_test2(machiene, press, press_scale)
	#speed = line_test(machiene, press)
	#test = drawing("glue_og.dxf", line_speed=3, line_pressure=3)
	#test = drawing("Line_Thickness_og.dxf", speed_dict=speed_dict, pressure_dict=pressure_dict)
	#test.draw(machiene)