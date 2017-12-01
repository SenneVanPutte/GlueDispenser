
import ezdxf
import time
from math import sqrt
import signal
import sys
import serial

def emergency_stop(signal, frame):
	global machine
	print "Emergency Stop sequence"
	machine.stop()
	exit(0)
	

if "verbose" in sys.argv:
	verbose=1
else:
	verbose=0


signal.signal(signal.SIGINT, emergency_stop)
#signal.pause()

class gcode():
	def __init__(self, serialport=None):
		self.x=-1
		self.y=-1
		self.speed=100 #mm/s
		self.zspeed=10 #mm/s on Z axis
		self.aspeed=10 #deg/s
		self.time_movingxy=0
		self.time_movingz=0
		self.time_glueing=0
		self.line_number=0
		if "serial" in sys.argv:
			
			self.serialport=serial.Serial(r"/dev/ttyUSB0", baudrate=115200, rtscts=True)
		else:
			self.serialport=None
	def send_line(self,line):
		if self.serialport and self.serialport.cts:
			self.serialport.write(line)
			ack=self.serialport.read() #might be blocked until command finishes ???
			print ack

	def send_bloc(self, bloc):
		self.line_number+=(10-self.line_number%10) #round the line number 
		for l in bloc.splitlines():
			txt="N{0:05} {1}".format(self.line_number,l)
			if verbose: print "===>\t",txt
			self.send_line(txt)
			if "step" in sys.argv: raw_input("press Enter to continue")
			self.line_number+=1
			self.line_number%=100000 # line number wrapping, (spec)
			
	def down(self):
		print "down"
		gcode="G1 Z10, {}".format(self.zspeed)
		t=1
		time.sleep(t)
		self.time_movingz+=t
		self.send_bloc(gcode)
	def up(self):
		print "up"
		gcode="G1 Z20, {}".format(self.zspeed)
		t=1
		time.sleep(t)
		self.time_movingz+=t
		self.send_bloc(gcode)
	
	def gotoxy(self, x,y):
		distance=sqrt((self.x-x)**2+(self.y-y)**2)
		print "goto {}, {}, ({}s)".format(x,y,distance/self.speed)
		gcode="G1 X{} Y{}, {}".format(x,y,self.speed)
		self.send_bloc(gcode)
		self.x=x
		self.y=y
		time.sleep(distance/self.speed)
		self.time_movingxy=distance/self.speed
		
	def glue(self, turns=1):
		print "glueing {}".format(turns)
		time.sleep(turns)
		gcode="G1 A{0}, {1}; {2} turns".format(turns*360.,self.aspeed, turns)
		self.send_bloc(gcode)
		self.time_glueing+=turns
	
	def init_code(self):
		#send initialisation sequence
		code="""G61 ;exact path model
		G21; select mm unit (just in case)
		G40 ; cancel cutter radius compensation
		G28.2 X0 Y0 Z0 A0 ;homing sequence
		G1 Z20 ;move Z to high position
		"""
		self.send_bloc(code)
	
	def closing_code(self):
		code=""
		self.send_bloc(code)
	def stop(self):
		gcode="M30"
		self.send_bloc(gcode)
		print "##### EMERGENCY STOP #####"


if __name__=="__main__":
	print "extract glue coordinates from DXF file"
	dwg=ezdxf.readfile("glue.dxf")
	mod=dwg.modelspace()
	lines=[]
	points=[]
	for e in mod:
		if e.dxftype() == 'LINE' and e.dxf.layer=="border":
			#print "LINE on layer: {}\n".format(  e.dxf.layer)
			print "start point: {}".format(  e.dxf.start)
			print "end point: {}".format(  e.dxf.end)
			lines.append([e.dxf.start, e.dxf.end])
		if e.dxftype() == 'POINT' and e.dxf.layer=="points":
			#print "Point on layer: {}".format(  e.dxf.layer)
			#print e, dir(e), dir(e.dxf)
			print "point: {}\n".format(  e.dxf.location)
			#print "end point: {}\n".format(  e.dxf.end)
			if e.dxf.location not in points: points.append(e.dxf.location)
		
	print "found {} lines, {} points".format(len(lines), len(points))
	print lines
	print points
	
	print "generate G code"
	start=time.time()
	machine=gcode()
	print "machine initialisation"
	machine.init_code()
	print "===> lines"
	if len(lines)>0:
		init_move=lines[0][0]
		machine.gotoxy(*init_move)
		machine.down()
	
	
	previous_point=lines[0][0]
	n=0
	for l in lines:
		n+=1
		print "{0:06.1f}\t {2}/{3} {1}".format(-start+time.time(),l,n,len(lines))
		startpoint=l[0]
		endpoint=l[1]
		if startpoint!=previous_point:
			machine.up()
			machine.gotoxy(*startpoint)
			machine.down()
		#goto end point
		machine.gotoxy(*endpoint)
		previous_point=endpoint
	machine.up()
	
	#sort points in X, then Y, then order them from the 1st with closest distance first
	
	print "lines done\n===> points"
	n=0
	for p in points:
		n+=1
		print "{0:06.1f}\t {2}/{3} {1}".format(-start+time.time(),p,n,len(points))
		machine.up()
		machine.gotoxy(*p)
		machine.down()
		machine.glue(1)
		machine.up()
		
	machine.gotoxy(0,0)
	print "{0:06.1f}\t END".format(time.time()-start)
	print "xy {}s".format(machine.time_movingxy)
	print "z {}s".format(machine.time_movingz)
	print "glueing {}s".format(machine.time_glueing)
	print "total {}".format(time.time()-start)
			