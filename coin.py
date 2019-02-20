from __future__ import print_function
from gcode_handler import gcode_handler
import datetime

if __name__ == "__main__":
	res = 30
	leng = 30.
	coin_file_name = "coin_"  + str(res) + "x" + str(res) + ".txt"
	coin_file = open(coin_file_name, "a+")
	coin_file.write("#\t ____COIN_PROBE____\n")
	print("#\t ____COIN_PROBE____\n")
	print("printing to " + coin_file_name)
	
	
	machiene = gcode_handler()
	machiene.init_code()
	machiene.gotoxy(100, 100)
	
	raw_input("place coin")
	pos_coin = machiene.probe_z(speed=100)
	coin_height = pos_coin[2] - 3
	machiene.down(coin_height)
	
	coin_file.write("#\t start time:" + datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + "\n")
	print("#\t start time:" + datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + "\n")

	progress = 1
	for ix in range(res):
		dx = ix*(leng/res)
		for iy in range(res):
			dy = iy*(leng/res)
			machiene.gotoxy(100 + dx, 100 + dy, speed=200)
			pos = machiene.probe_z(speed=25, up=coin_height)
			coin_file.write(str(pos) + "\n")
			if progress%20:
				print(str(progress) + ", " , end="")
			else:
				print(str(progress))
			progress += 1
			
	coin_file.write("#\t end time:" + datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + "\n")
	print("#\t end time:" + datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + "\n")
	coin_file.close()