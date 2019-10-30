from glueing_cfg import JIG_OFFSET_CFG, sum_offsets, JIG_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord, make_quick_func, drawing2
from scale_handler import scale_handler, delay_and_flow_regulation


if __name__ == '__main__':
	machiene = gcode_handler()
	machiene.init_code()
	
	machiene.gotoxy(36, 110)
	machiene.down(15)
	[x_s, y_s, z_s] = machiene.probe_z(speed=25)
	print(z_s)
	
	machiene.up()
	machiene.gotoxy(46, 130)
	machiene.down(15)
	[x_t, y_t, z_t] = machiene.probe_z(speed=25)
	print(z_t)
	print('Difference: ' + str(z_s - z_t))
	
	machiene.up()
	machiene.gotoxy(116, 130)
	machiene.down(15)
	[x_t, y_t, z_t] = machiene.probe_z(speed=25)
	print(z_t)
	print('Difference: ' + str(z_s - z_t))
	
	machiene.up()
	machiene.gotoxy(46, 200)
	machiene.down(15)
	[x_t, y_t, z_t] = machiene.probe_z(speed=25)
	print(z_t)
	print('Difference: ' + str(z_s - z_t))