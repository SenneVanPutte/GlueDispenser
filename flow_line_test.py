from scale_handler import scale_handler, measure_delay, delay_and_flow_regulation, delay_and_flow_regulation2
from gcode_handler import gcode_handler, drawing

import matplotlib
from matplotlib import pyplot

if __name__ == '__main__':
	machiene = gcode_handler()
	#machiene.init_code()
	
	scale = scale_handler() 
	#scale.conf_avg("b")
	#scale.calibrate()
	scale.zero()
	
	pressure = 4500 #blue needle glue 10 mg/s
	desired_flow = 5
	
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
	desired_press, delay_t, flow = delay_and_flow_regulation2(
								machiene, 
								scale, 
								[0, 0, 0], 
								pressure, 
								desired_flow, 
								precision=1, 
								duration=10, 
								threshold=15, 
								show_data=True
								)
								
	print('Desired pressure is '+str(desired_press) + ' mbar, delay is ' + str(delay_t) + ' s' )
	
	machiene.up()
	machiene.gotoxy(position=[0, 100])
	machiene.gotoxy(position=[100, 100])
	machiene.down(28)
	[x_st, y_st, z_st] = machiene.probe_z(speed=25)
	
	dist = 50.
	desired_glue_amount = 17
	time_travel = (desired_glue_amount+0.)/(flow + 0.)
	desired_speed = (dist*60./time_travel)
	print("Using: " + str(desired_speed/60.) + " mm/s, " + str(desired_press) + " mbar and " + str(flow) + " mg/s" )
	#machiene.gotoxy(position=[100, 110])
	#machiene.down(z_st - 0.2)
	#machiene.set_pressure(desired_press)
	#machiene.gotoxy(position=[100, 110+dist], speed=desired_speed)
	#machiene.stop_pressure()
	#machiene.gotoxy(position=[100, 110], speed=desired_speed)
	#machiene.up()
	#machiene.gotoxy(position=[100, 110+dist+10])
	
	prc = 0.9
	machiene.gotoxy(position=[100, 110+(2-prc)*dist/2.])
	machiene.down(z_st - 0.2)
	machiene.set_pressure(desired_press)
	machiene.wait(0.75)
	machiene.gotoxy(position=[100, 110+dist], speed=desired_speed*2)
	
	machiene.gotoxy(position=[100, 110], speed=desired_speed*2)
	machiene.gotoxy(position=[100, 110+prc*dist/2.], speed=desired_speed*2)
	machiene.stop_pressure()
	machiene.gotoxy(position=[100, 110+dist], speed=desired_speed/2.)
	machiene.gotoxy(position=[100, 110], speed=desired_speed/2.)
	machiene.up()
	machiene.gotoxy(position=[100, 110+dist+10])
	
	
	