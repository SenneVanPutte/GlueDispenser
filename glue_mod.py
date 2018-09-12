
import ezdxf
import time
from math import sqrt
import signal
import sys
import serial
import io
from threading import Thread

kill=0
MIN_OFFSET = [75, 100]
SPEED_DICT = {}
for i in range(5):
	SPEED_DICT[i+1] = 2000 - i*400 

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
			self.serialport_pnp = io.TextIOWrapper(io.BufferedRWPair(tg, tg))
			#TO DO: do something like this for the pressure regulation
			#gt=serial.Serial(bla)
			#self.serialport_press = io.TextIOWrapper(io.BufferedRWPair(gt, gt))
		else:
			self.serialport_pnp=None
			
		self.kill=0 #send exit signal to read thread
		self.command_done=0
		self.readthread = Thread(target=self.readState)
		#self.readthread.start()
	def readState(self):
		print "reading thread alive"
		global kill, command_done
		while not kill:
			line=self.serialport_pnp.readline()
			#if line: print line[:-1]
			if '"qr":32' in line:
				command_done=1

	def send_line(self,line):
		#if self.serialport_pnp and self.serialport_pnp.cts:
		if not "$" in line:
			self.serialport_pnp.write(unicode('{"gc":"'+line+'"}\n'))
		else:
			self.serialport_pnp.write(unicode(line))
		self.serialport_pnp.flush()
		#	time.sleep(0.5)
		#	ack=self.serialport_pnp.readline() #might be blocked until command finishes ???
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
				line=self.serialport_pnp.readline()
				#if line: print line,
			#print self.serialport_pnp.readborders()
			if "step" in sys.argv: raw_input("press Enter to continue")
			self.line_number+=1
			self.line_number%=100000 # line number wrapping, (spec)
			
	def down(self):
		t=time.time()
		#print "down"
		gcode="G1 Z20 F{}".format(self.zspeed)
		t=1
		#time.sleep(t)
		
		self.send_bloc(gcode)
		self.time_movingz+=(time.time()-t)
	def up(self):
		t=time.time()
		#print "up"
		gcode="G1 Z0 F{}".format(self.zspeed)
		t=1
		#time.sleep(t)
		
		self.send_bloc(gcode)
		self.time_movingz+=(time.time()-t)
	
	def gotoxy(self, x,y, speed=None):
		t=time.time()
		if speed is None:
			move_speed = self.speed
		else:
			move_speed = speed
		distance=sqrt((self.x-x)**2+(self.y-y)**2)
		#print "goto {}, {}, ({}s)".format(x,y,distance/move_speed)
		gcode="G1 X{} Y{} F{}".format(x,y,move_speed)
		self.send_bloc(gcode)
		self.x=x
		self.y=y
		#time.sleep(distance/self.speed)
		#self.time_movingxy=distance/self.speed
		self.time_movingxy+=(time.time()-t)
		
	def glue(self, turns=1):
		t=time.time()
		#print "glueing {}".format(turns)
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
		; PWM config for glue dispenser
		$p1frq=10000 ;10kHz
		$p1csl=0     ;lowest=0
		$p1csh=5700 ; highest in mbar
		$p1cpl=0.0
		$p1cph=1.0 ;for 1.0 duty cycle
		;M3 S<speed> to use
		;
		G61 ;e-xact path model
		G21; select mm unit (just in case)
		G40 ; cancel cutter radius compensation
		G28.2 X0 Y0 Z0 A0 ;homing sequence
		G1 Z0 F1000 ;move Z to high position
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
		gcode="""
		M5 ;stop glue
		M30"""
		global kill
		kill=1
		self.send_bloc(gcode)
		print "##### EMERGENCY STOP #####"

def draw_lines(lines, machine, offset=MIN_OFFSET, lines_w=None, set_pen=False):
		offset_test(offset)
		if lines_w is not None and len(lines) != len(lines_w): raise IOError("draw_lines: lines and lines_w must have same length")
		if len(lines) == 0: 
			print("draw_lines: no lines found.")
			return
		init_move=lines[0][0]
		machine.gotoxy(init_move[0] + offset[0], init_move[1] + offset[1])
		previous_point=lines[0][0]
		n=0
		machine.down()
		if set_pen:
			raw_input("-set pen")
		for i,l in enumerate(lines):
			n+=1
			startpoint=l[0]
			endpoint=l[1]
			if startpoint!=previous_point:
				machine.up()
				machine.gotoxy(startpoint[0] + offset[0], startpoint[1] + offset[1])
				machine.down()
			#goto end point
			if lines_w is None:
				machine.gotoxy(endpoint[0] + offset[0], endpoint[1] + offset[1])
			else:
				machine.gotoxy(endpoint[0] + offset[0], endpoint[1] + offset[1], SPEED_DICT[lines_w[i]])
			previous_point=endpoint
		machine.up()

def draw_dots(dots, machine, offset=MIN_OFFSET, set_pen=False):
		offset_test(offset)
		machine.up()
		machine.gotoxy(dots[0][0] + offset[0], dots[0][1] + offset[1])
	
		if set_pen:
			machine.down()
			raw_input("-set pen")
		n=0
		for p in dots:
			n+=1
			#print "{0:06.1f}\t {2}/{3} {1}".format(-start+time.time(),p,n,len(glue_dots))
			machine.up()
			machine.gotoxy(p[0] + offset[0], p[1] + offset[1])
			machine.down()
			machine.glue(1)
			machine.up()
		
def line_width_test( dxf_file_name, machine, offset=MIN_OFFSET):
		print("loading data from " + dxf_file_name)
		if dxf_file_name is None: 
			return 1
		dwg_lw=ezdxf.readfile(dxf_file_name)
		mod_lw=dwg_lw.modelspace()
	
		borders_lw=[]
		glue_lines_lw=[]
		lw_list = [] 
		lw_dict = {} 
		LW = None 
		for e in mod_lw:
			if e.dxftype() == 'LINE' and e.dxf.layer=="border":
				borders_lw.append([e.dxf.start, e.dxf.end])
			if e.dxftype() == 'LINE' and e.dxf.layer=="glue_lines":
				lw_list.append(e.dxf.lineweight)
				glue_lines_lw.append([e.dxf.start, e.dxf.end])
		glue_lw = lw_list
		lw_list.sort()
		print "appearing line widths: "
		for i,lw in enumerate(lw_list):
			lw_dict[lw] = i+1
			print "  line " + str(i+1) + " has width " + str(lw)

		nlw_list = [lw_dict[lw] for lw in lw_list]
	
		print "-drawing borders"
		machine.up()
		draw_lines(borders_lw, machine, offset=offset, set_pen=True)
		
		print "-glueing lines"
		draw_lines(glue_lines_lw, machine, offset=offset, lines_w=nlw_list)
		machine.gotoxy(offset[0], offset[1])
		
		chosen_lw = raw_input("Choose line width from 1 to 5: ")
		chosen_lw = int(chosen_lw)
		tries = 1
		while chosen_lw not in range(1,6) and tries < 3:
			print("Received " + str(chosen_lw) + " should be number between 1 and 5, " + str(3 - tries) + " tries left")
			chosen_lw = raw_input("Rechoose line width from 1 to 5: ")
			chosen_lw = int(chosen_lw)
			tries += 1
		
		if chosen_lw not in range(1,6): raise IOError("Linewidth not between 1 and 5")
		print "you chose " + str(chosen_lw)
	
		return chosen_lw

def load_board(dxf_file_name, chosen_lw):
	print("loading data from " + dxf_file_name)
	board = {}
	board["boarders"] = []
	board["glue_dots"] = []
	board["glue_lines"] = []
	board["glue_lines_w"] = []
	board["glue_zigzag"] = []
	board["glue_zigzag_w"] = []
	dwg=ezdxf.readfile(dxf_file_name)
	mod=dwg.modelspace()
	for e in mod:
		if e.dxftype() == 'LINE' and e.dxf.layer=="border":
			#print "LINE on layer: {}\n".format(  e.dxf.layer)
			#print "start point: {}".format(  e.dxf.start)
			#print "end point: {}".format(  e.dxf.end)
			board["boarders"].append([e.dxf.start, e.dxf.end])
		if e.dxftype() == 'LINE' and e.dxf.layer=="glue_lines":
			#print "LINE on layer: {}\n".format(  e.dxf.layer)
			#print "start point: {}".format(  e.dxf.start)
			#print "end point: {}".format(  e.dxf.end)
			board["glue_lines"].append([e.dxf.start, e.dxf.end])
			board["glue_lines_w"].append(chosen_lw)
		if e.dxftype() == 'LINE' and e.dxf.layer=="glue_zigzag":
			#print "LINE on layer: {}\n".format(  e.dxf.layer)
			#print "start point: {}".format(  e.dxf.start)
			#print "end point: {}".format(  e.dxf.end)
			board["glue_zigzag"].append([e.dxf.start, e.dxf.end])
			board["glue_zigzag_w"].append(chosen_lw)
		if e.dxftype() == 'POINT' and e.dxf.layer=="glue_dots":
			#print "Point on layer: {}".format(  e.dxf.layer)
			#print e, dir(e), dir(e.dxf)
			#print "point: {}\n".format(  e.dxf.location)
			#print "end point: {}\n".format(  e.dxf.end)
			if e.dxf.location not in board["glue_dots"]: board["glue_dots"].append(e.dxf.location)
	return board
	
def draw_board(board, machine, offset=MIN_OFFSET):
	print "-drawing borders"
	draw_lines(board["boarders"], machine, offset=offset, set_pen=True)
	print "-gluing lines"
	draw_lines(board["glue_lines"], machine, offset=offset, lines_w=board["glue_lines_w"])
	print "-gluing zigzag"
	draw_lines(board["glue_zigzag"], machine, offset=offset, lines_w=board["glue_zigzag_w"])
	print "-gluing dots"
	#draw_dots(board["glue_dots"], machine, offset=offset)
	
def offset_test(offset):
	if offset[0] < MIN_OFFSET[0]: raise ValueError("DANGER: x offset to low, nozzle will collide with rack.")
	if offset[1] < MIN_OFFSET[1]: print("WARNING: y offset lower then MIN_OFFSET[y], may draw out of range.")
	
def sum_offsets(offset1, offset2):
	if len(offset1) != len(offset2): raise ValueError("sum_offsets: offsets not of equal length")
	new_offset = []
	for i in range(len(offset1)):
		new_offset.append(offset1[i] + offset2[i])
	return new_offset
		
	

if __name__=="__main__":
	start = time.time()
	print "-----generate G code-----"
	machine=gcode()
	
	print "-----machine initialisation-----"
	machine.init_code()
	kill=1
	base_offset = [75, 100]
	board_offset = [175, 100]
	
	#off bulges 
	#base_offset = sum_offsets(base_offset, [300, 0])
	#board_offset = sum_offsets(board_offset, [300, 0])
	
	start_t = time.time()
	print "-----starting line width test-----"
	chosen_lw = line_width_test("Line_Thickness_og.dxf", machine, offset=base_offset)
	
	start_b = time.time()
	print "-----starting boards sequence-----"
	n_boards = int(raw_input("How many boards? (1 to 5): "))
	if n_boards not in range(1,6):
		print("Input was not in range, default to 1.")
		n_boards = 1
	board = load_board("glue_og.dxf", chosen_lw)
	print "start drawing boards"
	for i in range(n_boards):
		if i < 2:
			ib_offset = sum_offsets(board_offset, [150*i, 0])
			#ib_offset = [175 + 150*i, 100]
		else:
			ib_offset = sum_offsets(base_offset, [150*(i - 2), 150]) 
			#ib_offset = [75 + 150*(i - 2), 250]
		print "-board " + str(i + 1) + " in " + str(ib_offset)
		draw_board(board, machine, offset=ib_offset)
	print "boards drawn"
	
	machine.up()
	machine.gotoxy(0,0)
	end = time.time()
	print "-----recap-----"
	print "total time spend:\t {}s".format(end-start)
	print "width test time:\t {}s".format(start_b-start_t)
	print "board drawing time:\t {}s".format(end-start_b)
	print "xy {}s".format(machine.time_movingxy)
	print "z {}s".format(machine.time_movingz)
	print "glueing {}s".format(machine.time_glueing)
	print "total {}".format(time.time()-start)
			