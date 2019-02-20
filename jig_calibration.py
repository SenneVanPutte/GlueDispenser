from gcode_handler import gcode_handler

import time
def find_pos(machiene):
	pass
	
def find_angle(machiene):
	pass

class probe:
		def __init__(self, machine):
			self.machine=machine
			self.z=0
			self.x=0
			self.y=0
	#	def set_axis(self,axis="x+"):
			#x, y: axis
			# +/-: direction of probing
	#		self.axis=axis #not defined in constructor to avoid preconfig
		def probe_z(self,x,y,threshold=19,speed=30):
			self.machine.gotoxy(x,y)
			self.machine.down(15)
			self.pos=self.machine.probe_z(max_z=threshold+0.5, speed=25, up=15)
			time.sleep(0.5)
			self.machine.up()
			return self.pos
		def probe_edge(self, expected_x, expected_y, threshold, axis, step=1.0, speed=25):
				self.start_x=expected_x
				self.start_y=expected_y
				
				if "-" in axis: self.step=-step
				else: self.step=step
				if "x" in axis:self.start_x+=self.step #offset on the axis probed
				if "y" in axis:self.start_y+=self.step
				def next_pos(direction=1): #-1 for reverse
					if "x" in axis:  self.x+=self.step*direction
					if "y" in axis:  self.y+=self.step*direction
				edge_detected=0
				self.x=self.start_x
				self.y=self.start_y
				z_prev=0
				while(abs(self.step)>0.1):
					#self.machine.
					print("probe {0:6.3f},{1:6.3f}, step={2:6.3f}".format(self.x,self.y,self.step))
					x,y,z=self.probe_z(self.x,self.y,threshold,speed)
					print("Z={0:6.3f}".format(z))
					if not z_prev:z_prev=z
					if abs(z-z_prev)>0.25: 
						edge_detected=1
						print("edged detected at {0:6.3f},{1:6.3f},{2:6.3f}".format(*self.pos))
						next_pos(-2) # go one step back
						self.step/=2.0
						z_prev=0 #no previous measurement for next iteration
						if abs(self.step)<=0.1:break
					else: edge_detected=0
					next_pos(1)
				print("edge found around {0:6.3f},{1:6.3f},{2:6.3f}".format(*self.pos))
				return self.pos
						#self.machine.gotoxy()
					
				
	
def probe_y(machiene, start_x, start_y, threshold_h=18, dy=1, speed=50, up=15):
	if dy < 0.025:
		print("finished")
		return
	
	machiene.up()
	machiene.gotoxy(start_x, start_y, speed=speed)
	machiene.down(up)
	pos = machiene.probe_z(speed=50, up=up)
	print(pos)
	start_z = pos[2]
	new_z = pos[2]
	it = 1
	final_y = start_y
	while new_z < threshold_h:
		final_y = start_y + it*dy
		machiene.gotoxy(start_x, final_y, speed=speed)
		posy = machiene.probe_z(speed=25, up = start_z - 0.5)
		print(posy)
		new_z = posy[2]
		it += 1
	if final_y == start_y:
		print("move back")
		return probe_y(machiene, start_x, final_y - dy, threshold_h=threshold_h, dy=dy, speed=speed, up=up)
	elif dy < 0.1:
		print("edge found at " + str(final_y))
		return [start_x, final_y]
	else:
		print("next")
		return probe_y(machiene, start_x, final_y - dy, threshold_h=threshold_h, dy=(dy + 0.0)/4., speed=max((speed + 0.0)/2., 25), up=start_z - 0.5)

def probe_x(machiene, start_x, start_y, threshold_h=18, dx=1, speed=25, up=15):
	if dx < 0.025:
		print("finished")
		return
	
	machiene.up()
	machiene.gotoxy(start_x, start_y, speed=speed)
	machiene.down(up)
	pos = machiene.probe_z(max_z=threshold_h+1, speed=25, up=up)
	print(pos)
	start_z = pos[2]
	new_z = pos[2]
	it = 1
	final_x = start_x
	while new_z < threshold_h:
		final_x = start_x - it*dx
		machiene.gotoxy(final_x, start_y, speed=speed)
		posy = machiene.probe_z(max_z=threshold_h+1, speed=25, up = start_z - 0.5)
		print(posy)
		new_z = posy[2]
		it += 1
	if final_x == start_x:
		print("move back")
		return probe_x(machiene, final_x + dx, start_y, threshold_h=threshold_h, dx=dx, speed=speed, up=up)
	elif dx < 0.1:
		print("edge found at " + str(final_x))
		return [final_x, start_y]
	else:
		print("next")
		return probe_x(machiene, final_x + dx, start_y, threshold_h=threshold_h, dx=(dx + 0.0)/4., speed=max((speed + 0.0)/2., 25), up=start_z - 0.5)
		
if __name__ == "__main__":
	machiene = gcode_handler()
	machiene.init_code()
	
	
	prb=probe(machiene)
	
	prb.probe_edge(80,112,19,"y+")
	
	exit(0)
	
	# first y edge
	print("first y edge")
	machiene.gotoxy(80, 116)
	probe_y(machiene, 80, 116)
	machiene.up()
	
	# next y edge 140 mm further in x
	print("second y edge")
	machiene.gotoxy(220, 116)
	probe_y(machiene, 220, 116)
	machiene.up()
	
	# x edge
	print("first x edge")
	machiene.gotoxy(80, 116)
	probe_x(machiene, 80, 116, threshold_h=20, dx=4, up=17)
	machiene.up()
	
	print("second x edge")
	machiene.gotoxy(80, 214)
	probe_x(machiene, 80, 214, threshold_h=20, dx=4, up=17)