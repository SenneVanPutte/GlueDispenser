from gcode_handler import gcode_handler, drawing

if __name__ == "__main__":
	machiene = gcode_handler()	
	machiene.init_code()
	machiene.measure_tilt( scale_x, scale_y, scale_length, scale_width)
	
	cali_plat = drawing("scale_line_cal.dxf", line_speed=750, line_pressure=300)
	cali_plat.draw_lines(machiene) #boarders
	flow = 0
	drop_time = 2
	pressure = 300
	while flow > 2.5 or flow < 1.5: #2.5 or 1.5 mg/s
		#reset scale 
		cali_plat.drop_glue(machiene, drop_time, pressure)
		#measure mass
		#flow = mass/drop_time
		if flow <= 0: #or very low threshold value
			pressure += pressure
		elif flow > 2.5 or flow < 1.5:
			gain_factor = 2/flow
			pressure *= gain_factor
		print("Flow was " + str(flow) + ", new pressure = " + str(pressure))
		raw_input("Clean up your mess")
	