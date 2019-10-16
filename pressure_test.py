print("Import pending...")
from scale_handler import scale_handler, measure_delay, delay_and_flow_regulation
from gcode_handler import gcode_handler, drawing

import matplotlib
from matplotlib import pyplot
import datetime 
import time
import sys
import math

def log_file(f,txt):
	f.write("{0}\t{1}\n".format(time.time(),txt))

	
def weight_parts(scale,f):
	print("Weight parts")
	s=""
	n=0
	scale.read_port_h()
	while(not s):
		if raw_input("remove everything on scale or skip"): return
		time.sleep(5)
		scale.zero()
		mass=scale.read_port_h()
		while(not mass[0]):
			mass=scale.read_port_h()
		print(mass)
		log_file(f,"part {0} zero={1}".format(n,mass))
		raw_input("place part {0} on scale".format(n))
		time.sleep(5)
		mass=scale.read_port_h()
		log_file(f,"part {0} mass={1}".format(n,mass))
		print mass
		s=raw_input("end?")
		n+=1
	print("replace cup on scale")
	
	
if __name__ == '__main__':
	print("starting, please wait...")
	f=open("pressure.log","a")
	machiene = gcode_handler()
	if "init" in sys.argv:machiene.init_code()
	log_file(f,"\n\n\n"+str(datetime.datetime.now()))
	scale = scale_handler() 
	#scale.conf_avg("d")
	#scale.calibrate()
	#scale.zero()
	print("start "+str(datetime.datetime.now()))
	pressure = 100#00 #blue needle glue 10 mg/s
	for p in range(10,80,2):
		print (p)
		machiene.set_pressure(p,no_flush=False)
		time.sleep(1)
		print(scale.read_port_h())
	machiene.stop_pressure()
	time.sleep(0.1)
	print(scale.read_port_h())
	#desired_flow = 5
	#if "weight" in sys.argv:machiene.gotoxy(position=[0,100])
	#if "weight" in sys.argv:weight_parts(scale,f)
	#4/5/1800 for scale
	#delay, delay_up, delay_dn, press_guess, data = measure_delay(machiene, scale, [0, 0, 0], pressure, duration=3, threshold=30, desired_flow=desired_flow)
	#print('Delay is ' + str(delay) + ', uncert window: [' + str(delay_dn) + ', ' + str(delay_up)  + ']'  ) 
	#scale.plot_data(data)
	
	#raw_input('Starting flow reg')
	#init_pressure = pressure
	#if press_guess is not None: init_pressure = press_guess

	#desired_press, delay_t = delay_and_flow_regulation(
	#							machiene, 
	#							scale, 
	#							[0, 0, 0], 
	#							pressure, 
	#							desired_flow, 
	#							precision=1, 
	#							duration=10, 
	#							threshold=10, 
	#							show_data=True
	#							)
	exit(0)
	scale.zero()
	while( math.fabs(scale.read_mass())>0.1):
		print (scale.read_mass())
		time.sleep(1)
		#scale.read_port_h()
	desired_press, delay_t, flow = delay_and_flow_regulation2(
								machiene, 
								scale, 
								[0, 0, 0], 
								pressure, 
								desired_flow, 
								precision=104.5, 
								duration=10, 
								threshold=1, 
								show_data=True
								)
								
	print('Desired pressure is '+str(desired_press) + ' mbar, delay is ' + str(delay_t) + ' s' )
	log_file(f,"pressure/flow:\n{0:.3f}, {1:.3f}".format(desired_press,flow))
	
	# print("1st line",datetime.datetime.now())
	# machiene.up()
	# #machiene.gotoxy(position=[0, 100])
	# machiene.gotoxy(position=[100, 95])
	# machiene.down(28)
	# [x_st, y_st, z_st] = machiene.probe_z(speed=50,up=5)
	
	dist = 84. #compute for standard long line
	desired_glue_amount = 17
	time_travel = (desired_glue_amount+0.)/(flow + 0.)
	desired_speed = (dist*60./time_travel)
	print("Using: " + str(desired_speed/60.) + " mm/s, " + str(desired_press) + " mbar and " + str(flow) + " mg/s" )
	log_file(f,"speed: {0:.3f} mm/s, pressure: {1:.3f} mbar, flow: {2:.3f}".format(desired_speed,desired_press,flow))
	#machiene.gotoxy(position=[100, 110])
	#machiene.down(z_st - 0.2)
	#machiene.set_pressure(desired_press)
	#machiene.gotoxy(position=[100, 110+dist], speed=desired_speed)
	#machiene.stop_pressure()
	#machiene.gotoxy(position=[100, 110], speed=desired_speed)
	#machiene.up()
	#machiene.gotoxy(position=[100, 110+dist+10])
	
	# prc = 0.66
	# machiene.gotoxy(position=[100, 95+dist*2/3.])
	# machiene.down(z_st - 0.2)
	# machiene.set_pressure(desired_press)
	# machiene.wait(0.75)
	# machiene.gotoxy(position=[100, 95+dist], speed=desired_speed*2)
	
	# machiene.gotoxy(position=[100, 95], speed=desired_speed*2)
	# machiene.gotoxy(position=[100, 95+dist*1/3.], speed=desired_speed*2)
	# machiene.stop_pressure()
	# machiene.gotoxy(position=[100, 95+dist], speed=desired_speed/2.)
	# machiene.gotoxy(position=[100, 95], speed=desired_speed/2.)
	# machiene.up()
	
	# print("2nd line",datetime.datetime.now())
	# #2nd line
	# dist=10.
	# machiene.gotoxy(position=[110,74+95+dist*2/3.])
	# machiene.down(z_st - 2)
	# [x_st, y_st, z_st] = machiene.probe_z(speed=50,up=5)
	# machiene.down(z_st - 0.2)
	# machiene.set_pressure(desired_press)
	# machiene.wait(0.75)
	
	# machiene.gotoxy(position=[110, 95+74+dist], speed=desired_speed*2)
	
	# machiene.gotoxy(position=[110, 95+74], speed=desired_speed*2)
	# machiene.gotoxy(position=[110, 95+74+dist*1/3.], speed=desired_speed*2)
	# machiene.stop_pressure()
	# machiene.gotoxy(position=[110, 95+74+dist], speed=desired_speed/2.)
	# machiene.gotoxy(position=[110, 95+74], speed=desired_speed/2.)
	# machiene.up()
	line=0
	def draw_lineo(origx,origy,length,desired_speed,desired_press):
		global line
		global f
		#3rd line 120,95,84
		print("draw line {0} at {1}".format(line,datetime.datetime.now()))
		log_file(f,"draw line {0} at {1}, x={2}, y={3}, l={4}".format(line,datetime.datetime.now(),origx,origy,length))
		line+=1
		machiene.up()
		machiene.gotoxy(position=[origx, origy])
		machiene.down(28)
		[x_start, y_start, z_start] = machiene.probe_z(speed=25,up=5)
		print (x_start, y_start, z_start)
		machiene.gotoxy(position=[origx, origy+length])
		machiene.down(28)
		[x_stop, y_stop, z_stop] = machiene.probe_z(speed=25,up=5)
		print (x_stop, y_stop, z_stop)
		dist=length
		fly_h=0.3
		machiene.down(z_start - 2)
		machiene.gotoxy(position=[origx, origy+dist*2/3.])
		machiene.down(z_start - fly_h)
		machiene.set_pressure(desired_press)
		machiene.wait(0.75)
		machiene.gotoxyz(position=[origx, origy+dist,z_stop-0.3], speed=desired_speed*2)
		
		machiene.gotoxy(position=[origx, origy], speed=desired_speed*2)
		machiene.gotoxy(position=[origx, origy+dist*1/3.], speed=desired_speed*2)
		machiene.stop_pressure()
		machiene.gotoxy(position=[origx, origy+dist], speed=desired_speed)
		machiene.gotoxy(position=[origx, origy], speed=desired_speed)
		machiene.gotoxy(position=[origx+0.5, origy], speed=desired_speed)
		machiene.gotoxy(position=[origx+0.5, origy+dist], speed=desired_speed)
		machiene.gotoxy(position=[origx-0.5, origy+dist], speed=desired_speed)
		machiene.gotoxy(position=[origx-0.5, origy], speed=desired_speed)
		machiene.up()
	
		#machiene.gotoxy(position=[origx+10,80+origy])

		
	def draw_line(origx,origy,length,desired_speed,desired_press):
		global line
		global f
		#3rd line 120,95,84
		print("draw line {0} at {1}".format(line,datetime.datetime.now()))
		log_file(f,"draw line {0} at {1}, x={2}, y={3}, l={4}".format(line,datetime.datetime.now(),origx,origy,length))
		line+=1
		machiene.up()
		#mesure stqrt point
		machiene.gotoxy(position=[origx, origy])
		machiene.down(28)
		[x_start, y_start, z_start] = machiene.probe_z(speed=25,up=28)
		print (x_start, y_start, z_start)
		#mesure endpoint
		machiene.gotoxy(position=[origx, origy+length])
		machiene.down(28)
		[x_stop, y_stop, z_stop] = machiene.probe_z(speed=25,up=28)
		print (x_stop, y_stop, z_stop)
		dist=length
		fly_h=0.3
		#machiene.down(z_start - 2)
		#machiene.gotoxy(position=[origx, origy])
		machiene.down(z_stop - 2)
		machiene.gotoxyz(position=[origx, origy+dist,z_stop-fly_h])#desired_speed*2)
		machiene.set_pressure(desired_press)
		machiene.wait(0.75)
		
		start_pos=[origx, origy,z_start-fly_h]
		stop_pos=[origx, origy+dist,z_stop-fly_h]
		machiene.gotoxyz(position=start_pos, speed=desired_speed)
		#machiene.gotoxy(position=[origx, origy+dist*1/3.], speed=desired_speed*2)
		machiene.stop_pressure()
		machiene.gotoxyz(position=stop_pos, speed=desired_speed)
		machiene.gotoxyz(position=start_pos, speed=desired_speed)
		machiene.gotoxyz(position=[origx+0.5, origy,z_start-fly_h], speed=desired_speed)
		machiene.gotoxyz(position=[origx+0.5, origy+dist,z_stop-fly_h], speed=desired_speed)
		machiene.gotoxyz(position=[origx-0.5, origy+dist,z_stop-fly_h], speed=desired_speed)
		machiene.gotoxyz(position=[origx-0.5, origy,z_start-fly_h], speed=desired_speed)
		machiene.up()
		
		
		
	draw_line(100,98,84,desired_speed,desired_press)

	draw_line(110,98,10,desired_speed,desired_press)

	draw_line(120,98,84,desired_speed,desired_press)

	draw_line(140,98,84,desired_speed*3,desired_press)

	draw_line(150,98,10,desired_speed*3,desired_press)

	draw_line(160,98,84,desired_speed*3,desired_press)
	print("done at {1}".format(line,datetime.datetime.now()))
	weight_parts(scale,f)