from gcode_handler import gcode_handler


if __name__ == "__main__":
	machiene = gcode_handler()	
	#machiene.stop_pressure()
	
	machiene.init_code()
	machiene.gotoxy(100, 100)
	z = machiene.probe_z()
	#machiene.measure_tilt(100, 70, 100, 130)
	machiene.measure_tilt_3p([100, 70], [200, 70], [100, 200])
	machiene.gotoxy(100, 100)
	machiene.down(z - 3)
	machiene.gotoxy(100, 200, do_tilt=True)
	#machiene.probe_z()
	#machiene.gotoxy(100, 100)
	#machiene.send_bloc("G38.2 F100 Z60")
	#machiene.probe_z()
	#machiene.down(20)
	#machiene.gotoxy(100, 200)
	#machiene.probe_z()
	#print("End is reached by python")
	#machiene.probe_z()
	
	
	