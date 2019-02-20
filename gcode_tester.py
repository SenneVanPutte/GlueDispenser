from gcode_handler import gcode_handler
from threading import Thread
import time
import datetime

if __name__ == "__main__":
	file = open("jig_height_probe.txt", "a+")
	file.write("#\t" + datetime.datetime.now().strftime("%y-%m-%d-%H-%M") + "\n")
	file.write("#\t" + "speed = 25" + "\n")
	machiene = gcode_handler()	
	
	machiene.init_code()
	
	
	machiene.send_bloc("G1 X250 Y200 F2000")
	#machiene.send_bloc("G28.2 Z0 Y0 X0")
	#machiene.send_bloc("$3tr=200")
	machiene.send_bloc("G28.2 Z0")
	#machiene.send_bloc("G1 Z0")
	#machiene.send_bloc("$3mi=1")
	#machiene.send_bloc("G38.2 F10 Z50")
	
	z = machiene.probe_z(speed=100)
	for i in range(100):
		#machiene.down(z[2] - 1)
		zz = machiene.probe_z(speed=25, up=z[2] - 1)
		file.write(str(zz) + "\n")
		
		print(zz)
		#raw_input("next iteration (current = " + str(i) + " )")
	file.close()
		
	
	
	
	
	
	