from glueing_cfg import MIN_OFFSET, BOARDS_CFG
from gcode_handler import gcode_handler, drawing

if __name__ == "__main__":
	machiene = gcode_handler()
	machiene.init_code()
	#test = drawing("board_og.dxf", offset=BOARDS_CFG["offsets"]["1"], line_speed=400, line_pressure=300)
	#test = drawing("board2.5_og.dxf", offset=BOARDS_CFG["offsets"]["1"], line_speed=400, line_pressure=300)
	test = drawing("board3_og.dxf", offset=BOARDS_CFG["offsets"]["1"],hight=30, line_speed=400, line_pressure=300)
	#test = drawing("Line_Thickness_og.dxf", speed_dict=speed_dict, pressure_dict=pressure_dict)
	test.draw(machiene)
	machiene.gotoxy(300, 250)