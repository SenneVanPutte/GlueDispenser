
import ezdxf
import time
from math import sqrt
import signal
import sys
import serial
import io
from threading import Thread

kill=0


def emergency_stop(signal, frame):
	global machine
	print "Emergency Stop sequence"
	machine.stop()
	kill=1
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
		self.speed=2000 #mm/min
		self.zspeed=2000 #mm/min on Z axis
		self.aspeed=10 #deg/min
		self.time_movingxy=0
		self.time_movingz=0
		self.time_glueing=0
		self.line_number=0
		self.alpha=0 #alpha angle of the machine
		if "serial" in sys.argv:
			
			tg=serial.Serial(r"COM3", baudrate=115200, xonxoff=True, timeout=0.5)
			self.serialport = io.TextIOWrapper(io.BufferedRWPair(tg, tg))
		else:
			self.serialport=None
			
		self.kill=0 #send exit signal to read thread
		self.command_done=0
		self.readthread = Thread(target=self.readState)
		#self.readthread.start()
	def readState(self):
		print "reading thread alive"
		global kill, command_done
		while not kill:
			line=self.serialport.readline()
			if line: print line[:-1]
			if '"qr":32' in line:
				command_done=1

	def send_line(self,line):
		#if self.serialport and self.serialport.cts:
		print line
		if not "$" in line:
			self.serialport.write(unicode('{"gc":"'+line+'"}\n'))
		else:
			self.serialport.write(unicode(line))
		self.serialport.flush()
		#	time.sleep(0.5)
		#	ack=self.serialport.readline() #might be blocked until command finishes ???
		#	print ack

	def send_bloc(self, bloc):
		self.line_number+=(10-self.line_number%10) #round the line number 
		for l in bloc.splitlines():
			if "$" not in l: #if config line
				txt="N{0:05} {1}".format(self.line_number,l)
			else:
				txt=l
			#global command_done
			
			#if '"qr":32' in line:
			#	command_done=1
			#while (not command_done):
			#	time.sleep(0.1)
			#command_done=0 #we start a new command
			if verbose: print "===>\t",txt
			self.send_line(txt)
			#time.sleep(0.5)
			line="x"
			while(line):#'"qr":32' not in line and "$" not in line and "ok" not in line):
				line=self.serialport.readline()
				if line: print line,
			#print self.serialport.readlines()
			if "step" in sys.argv: raw_input("press Enter to continue")
			self.line_number+=1
			self.line_number%=100000 # line number wrapping, (spec)
			
	def down(self):
		t=time.time()
		print "down"
		gcode="G1 Z20 F{}".format(self.zspeed)
		t=1
		#time.sleep(t)
		
		self.send_bloc(gcode)
		self.time_movingz+=(time.time()-t)
	def up(self):
		t=time.time()
		print "up"
		gcode="G1 Z10 F{}".format(self.zspeed)
		t=1
		#time.sleep(t)
		
		self.send_bloc(gcode)
		self.time_movingz+=(time.time()-t)
	
	def gotoxy(self, x,y):
		t=time.time()
		distance=sqrt((self.x-x)**2+(self.y-y)**2)
		print "goto {}, {}, ({}s)".format(x,y,distance/self.speed)
		gcode="G1 X{} Y{} F{}".format(x,y,self.speed)
		self.send_bloc(gcode)
		self.x=x
		self.y=y
		#time.sleep(distance/self.speed)
		#self.time_movingxy=distance/self.speed
		self.time_movingxy+=(time.time()-t)
		
	def glue(self, turns=1):
		t=time.time()
		print "glueing {}".format(turns)
		#time.sleep(turns)
		self.alpha=self.alpha+360.0*turns
		gcode="G0 A{0} F{1}; {2} turns".format(self.alpha,self.aspeed, turns)
		self.send_bloc(gcode)
		self.time_glueing+=(time.time()-t)
		
	
	def init_code(self):
		#send initialisation sequence
		code="""$ex=1
		$ej=0
		$ec=0
		$ee=1
		$jv=3
		$js=1
		G61 ;e-xact path model
		G21; select mm unit (just in case)
		G40 ; cancel cutter radius compensation
		G28.2 X0 Y0 Z0 A0 ;homing sequence
		G1 Z10 F1000 ;move Z to high position
		G1 X300 Y250 F10000; move to paper page
		"""
		self.send_bloc(code)
	
	def home(self):
		self.send_bloc("G28.2 X0 Y0 Z0 A0")
	
	def closing_code(self):
		code="""G1 Z10 F1000 ;move Z to high position
		G1 X300 Y250 F10000; move to paper page"""
		self.send_bloc(code)
	def stop(self):
		gcode="M30"
		global kill
		kill=1
		self.send_bloc(gcode)
		print "##### EMERGENCY STOP #####"


if __name__=="__main__":
	print "extract glue coordinates from DXF file"
	dwg=ezdxf.readfile("glue.dxf")
	mod=dwg.modelspace()
	borders=[]
	glue_dots=[]
	glue_lines=[]
	for e in mod:
		if e.dxftype() == 'LINE' and e.dxf.layer=="border":
			#print "LINE on layer: {}\n".format(  e.dxf.layer)
			print "start point: {}".format(  e.dxf.start)
			print "end point: {}".format(  e.dxf.end)
			borders.append([e.dxf.start, e.dxf.end])
		if e.dxftype() == 'LINE' and e.dxf.layer=="glue_lines":
			#print "LINE on layer: {}\n".format(  e.dxf.layer)
			print "start point: {}".format(  e.dxf.start)
			print "end point: {}".format(  e.dxf.end)
			glue_lines.append([e.dxf.start, e.dxf.end])
		if e.dxftype() == 'POINT' and e.dxf.layer=="glue_dots":
			#print "Point on layer: {}".format(  e.dxf.layer)
			#print e, dir(e), dir(e.dxf)
			#print "point: {}\n".format(  e.dxf.location)
			#print "end point: {}\n".format(  e.dxf.end)
			if e.dxf.location not in glue_dots: glue_dots.append(e.dxf.location)
	
	print "found {} borders, {} glue_dots".format(len(borders), len(glue_dots))
	print borders
	print glue_dots
	
	print "generate G code"
	start=time.time()
	machine=gcode()
	
	print "machine initialisation"
	machine.init_code()
	kill=1
	#exit(0)
	print "===> borders"
	machine.up()
	if len(borders)>0:
		init_move=borders[0][0]
		machine.gotoxy(*init_move)
		
	
	
	previous_point=borders[0][0]
	n=0
	machine.down()
	raw_input("set pen")
	for l in borders:
		n+=1
		print "{0:06.1f}\t {2}/{3} {1}".format(-start+time.time(),l,n,len(borders))
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
	
	#sort glue_dots in X, then Y, then order them from the 1st with closest distance first
	
	print "borders done\n===> glue_dots"
	n=0
	for p in glue_dots:
		n+=1
		print "{0:06.1f}\t {2}/{3} {1}".format(-start+time.time(),p,n,len(glue_dots))
		machine.up()
		machine.gotoxy(*p)
		machine.down()
		machine.glue(1)
		machine.up()
	
	machine.up()
	machine.gotoxy(0,0)
	print "{0:06.1f}\t END".format(time.time()-start)
	print "xy {}s".format(machine.time_movingxy)
	print "z {}s".format(machine.time_movingz)
	print "glueing {}s".format(machine.time_glueing)
	print "total {}".format(time.time()-start)
			