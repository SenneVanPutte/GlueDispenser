
from gcode_handler import gcode_handler


if __name__ == "__main__":
	machiene = gcode_handler()
	#machiene.set_pressure(3000, no_flush=False)
	#raw_input("dumped?")
	#machiene.stop_pressure()
	
	
	machiene.init_code()
	print( "75, 100")
	machiene.gotoxy(100, 100)
	
	print("first square")
	machiene.set_pressure(300)
	#machiene.wait(1)
	machiene.down(40)
	#raw_input("set")
	print( "75, 200")
	machiene.gotoxyz(100, 300, 40.5, 1000)
	#raw_input("see diff")
	print( "150, 200")
	machiene.gotoxyz(300, 300, 40.5, 1000)
	print( "150, 100")
	machiene.gotoxyz(300, 100, 40, 1000)
	#raw_input("see diff")
	print( "75, 100")
	machiene.gotoxyz(100, 100, 40, 1000)
	machiene.up()
	#machiene.wait(1)
	machiene.stop_pressure()
	
	#machiene.wait(2)
	"""
	print("second square")
	machiene.set_pressure(300, glue_delay=10)
	print( "75, 200")
	machiene.gotoxy(75, 200)
	print( "150, 200")
	machiene.gotoxy(150, 200)
	print( "150, 100")
	machiene.gotoxy(150, 100)
	print( "75, 100")
	machiene.gotoxy(75, 100)
	machiene.stop_pressure(glue_delay=10)
	"""
	#machiene.wait(0.1)
	#machiene.wait(0.1)
	#print("test")
	
	machiene.close()
	