from gcode_handler import gcode_handler



if __name__ == "__main__":
	machiene = gcode_handler()
	machiene.set_pressure(5000, no_flush=False)
	raw_input("dumped?")
	machiene.stop_pressure()