from glueing_cfg import MIN_OFFSET, BOARDS_CFG, TABLE_HEIGHT
from gcode_handler import gcode_handler, drawing
from glue_calibration_multi import line

if __name__ == "__main__":
	machiene = gcode_handler()
	machiene.init_code()
	#test = drawing("board_og.dxf", offset=BOARDS_CFG["offsets"]["1"], line_speed=400, line_pressure=300)
	#test = drawing("board2.5_og.dxf", offset=BOARDS_CFG["offsets"]["1"], line_speed=400, line_pressure=300)
	test = drawing("board_m_og.dxf", offset=BOARDS_CFG["offsets"]["1"], line_speed=1000, line_pressure=64)
	answer = raw_input("Do you want to do a boarder check? (y/n)")
	if answer == "y":
		do_boarder = True
	else:
		do_boarder = False
	answer = raw_input("Do you want to draw zigzags? (y/n)")
	if answer == "y":
		do_zigzag = True
	else:
		do_zigzag = False
	#test = drawing("Line_Thickness_og.dxf", speed_dict=speed_dict, pressure_dict=pressure_dict)
	line(machiene, 64, speed=1000, x1=400, y1=200, x2=400, y2=120, height=TABLE_HEIGHT, set_pen=True)
	test.draw(machiene, boarders=do_boarder, zigzag=do_zigzag)
	machiene.gotoxy(300, 250)