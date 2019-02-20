import ezdxf
import time
import datetime
from math import sqrt
import signal
import sys
import serial
import io
import json
import ast
from threading import Thread
import Queue
from glueing_cfg import BOARDS_CFG, ST_CFG, MIN_OFFSET
#3231 phone yannick

class gcode_handler():
	"""
	Connection to PnP, send to and receive from to PnP, handle the Gcode
	"""
	def __init__(self, serialport=None):
		self.x=0
		self.y=0
		self.z=0
		self.speed=2000 #mm/min
		self.zspeed=500 #mm/min on Z axis
		self.aspeed=10 #deg/min
		self.time_movingxy=0
		self.time_movingz=0
		self.time_glueing=0
		self.line_number=0
		self.alpha=0 #alpha angle of the machine
		self.glue_start=None
		self.is_glueing=False
		self.time_out = 0.5
		self.time_out_short = 0.01
		if "noserial" in sys.argv:
			self.serialport_pnp=None
		else:
			tg=serial.Serial(r"COM3", baudrate=115200, xonxoff=True, timeout=self.time_out)
			self.serial_p = tg
			self.serialport_pnp = io.TextIOWrapper(io.BufferedRWPair(tg, tg))
		
		self.kill=False #send exit signal to read thread
		self.command_done=0
		self.glue_thread=None
		self.readthread = Thread(target=self.readState)
		self.do_flush = True
		self.reading_state = False
		self.tilt_map = {}
		self.tilt_map["x_tilt"] = 0
		self.tilt_map["y_tilt"] = 0
		self.tilt_map_og = [0, 0]
		
		self.log_file = open("gcode.log", "w+")
		self.log_file.write("#\t ____START_G_CODE_SESSION____\n")
		self.log_file.write("#\t TIME: " + datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + "\n")
		
		
		signal.signal(signal.SIGINT, self.emergency_stop)
		
	def read_buffer(self):
		response = self.serialport_pnp.readline()
		print(response)
	
	def probe_z(self, max_z=48, speed=200, up=0):
		q = Queue.Queue()
		probe_thread = Thread(target=self.wait_probe_stop, args=(q,))
		probe_thread.setDaemon(True)
		probe_thread.start()
		#self.send_bloc("$zsx=1")
		time.sleep(0.5)
		self.send_bloc("G38.2 F{} Z{}".format(speed, max_z))
		#self.send_bloc("G1 X0", capture_response=False)
		probe_thread.join()
		position = q.get()
		#print("retrieved z value is " + str(z))
		
		self.send_bloc("$zsx=0")
		time.sleep(0.5)
		self.down(up)
		#time.sleep(5)
		self.send_bloc("$zsx=1 ")
		
		return position
		
	def wait_probe_stop(self, queue):
		start = time.time()
		between = time.time()
		time_out = 4
		probe_stopped = False
		was_moving = False
		temp_z = 0
		while not probe_stopped:
			#if round(time.time() - start) - time.time() - start < 0.1: self.send_bloc("$sr")
			response = self.serialport_pnp.readline()
			if not response == unicode(""): 
				self.log_file.write("probe thread read: " +response)
				#print( "absolut time:" + str(str(time.time() - start)) + ", relative time: " + str(time.time() - between))
				between = time.time()
			
			try:
				resp_dict = ast.literal_eval(response)
			except:
				resp_dict = {}
			if "r" in resp_dict and "prb" in resp_dict["r"]:
				probe_stopped = True
				#print("Probe stopped at " + str(resp_dict["r"]["prb"]["z"]))
				queue.put([resp_dict["r"]["prb"]["x"], resp_dict["r"]["prb"]["y"], resp_dict["r"]["prb"]["z"]])
				self.log_file.write("prb\n")
				return
			elif "sr" in resp_dict and "posz" in resp_dict["sr"]:
				temp_z = [resp_dict["sr"]["posx"], resp_dict["sr"]["posy"], resp_dict["sr"]["posz"]]
				if "stat" in resp_dict["sr"] and resp_dict["sr"]["stat"] == 7 and not was_moving:
					was_moving = True
				if "stat" in resp_dict["sr"] and resp_dict["sr"]["stat"] == 3 and was_moving:
					probe_stopped = True
					#print("Probe stopped at " + str(resp_dict["sr"]["posz"]))
					queue.put([resp_dict["sr"]["posx"], resp_dict["sr"]["posy"], resp_dict["sr"]["posz"]])
					self.log_file.write("stat\n")
					return
			
			if time.time() - between > time_out:
				print("Warning: Waiting for probe stop timed out after " + str(time_out) + " seconds of no response")
				#self.send_bloc("$sr", capture_response=False)
				#response = self.serialport_pnp.readline()
				#print("Last response was: ", response)
				print("Z pushed was: ", temp_z)
				probe_stopped = True
				queue.put(temp_z)
				return
			time.sleep(0.1)
	
	def stop_reading(self):
		self.reading_state = False
	
	def wait_empty_queue(self):
		#print("Waiting q thread started")
		start = time.time()
		between = time.time()
		#time_out = 60
		time_out = 4
		queue_empty = False
		first_time = True
		was_moving = False
		while not queue_empty:
			response = self.serialport_pnp.readline()
			if not response == unicode(""): 
				#print(response)
				between = time.time()
			try:
				resp_dict = ast.literal_eval(response)
			except:
				resp_dict = {}
			if "qr" in resp_dict and resp_dict["qr"] == 32:
				if first_time: first_time = False
				else:
					queue_empty == True
					return
			elif "sr" in resp_dict and "stat" in resp_dict["sr"]:
				if resp_dict["sr"]["stat"] > 3 and not was_moving: was_moving = True
				if resp_dict["sr"]["stat"] == 3 and was_moving:
					queue_empty = True
					return
			#if "f" in resp_dict and resp_dict["f"][2] == 19:
			#	queue_empty == True
			#	return
			if time.time() - between > time_out:
				print("Warning: Waiting for empty queue timed out after " + str(time_out) + " seconds of no response")
				#print("Last response was: ", response)
				queue_empty == True
				return
			time.sleep(0.1)
	
	def readState(self):
		print "reading thread alive"
		global kill, command_done
		while not kill:
			line=self.serialport_pnp.readline()
			if '"qr":32' in line:
				command_done=1

	def send_line(self, line, no_wait=False):
		#if "$p1" in line: no_wait = True
		if not "$" in line:
			lines = line.split(";")
			send_str = '{"gc":"'+lines[0].replace("\t", "")+'"}\n'
			self.serialport_pnp.write(unicode(send_str))
			#print("send: ", unicode(send_str))
		else:
			#lines=line.split("=")
			#lines[1] = lines[1].split(";")
			#send_str = '{"' + lines[0].replace("$", "").replace(" ", "").replace("\t", "") + '":' + lines[1][0].strip(" ") + '}'
			lines=line.split(";")
			send_str = lines[0].replace(" ", "").replace("\t", "")
			self.serialport_pnp.write(unicode(send_str))
			#print("send: ", unicode(send_str))
			if not no_wait: self.send_line("G4 P0.2")
		if self.do_flush:
			self.serialport_pnp.flush()
			#response = self.serialport_pnp.readline()
			#print("response: ", response)
			#print("_______")
	
	def flush_on(self):
		self.serialport_pnp.flush()
		self.do_flush = True
		
	def flush_off(self):
		self.do_flush = False

	def send_bloc(self, bloc, no_wait=False, capture_response=True):
		#self.line_number+=(10-self.line_number%10) #round the line number 
		#print("bloc received: ", bloc)
		for l in bloc.splitlines():
			if "$" not in l: #if config line
				txt="N{0:05} {1}".format(self.line_number,l)
			else:
				txt=l
			self.send_line(txt, no_wait)
			line="x"
			responded = True
			if "$" in l: 
				responded = False
				test_str = "[" + l.split(";")[0].split("=")[0].replace("$", "").replace(" ", "").replace("\t", "") + "]"
				#print("test str", test_str)
			while ((line) and not self.kill or not responded) and capture_response:
				line=self.serialport_pnp.readline()
				if not responded: 
					if test_str in line:
						responded = True
				try:
					resp_dict = ast.literal_eval(line)
				except:
					resp_dict = {}
				if "er" in resp_dict: 
					print("######--WARNING--######")
					print(l, line)
				if not line == unicode(""):
					self.log_file.write("send bloc read: "+ line)
			if "step" in sys.argv: raw_input("press Enter to continue")
			self.line_number+=1
			self.line_number%=100000 # line number wrapping, (spec)
			
	def down(self, hight=BOARDS_CFG['hight_1'], do_tilt=False):
		delta_x = self.x - self.tilt_map_og[0]
		delta_y = self.y - self.tilt_map_og[1]
		if do_tilt:
			z = hight + delta_x*self.tilt_map["x_tilt"] + delta_y*self.tilt_map["y_tilt"]
		else:
			z = hight
		gcode="G1 Z{} F{}".format(z, self.zspeed)
		t=time.time()
		
		self.send_bloc(gcode)
		self.z=z
		self.time_movingz+=(time.time()-t)
		
	def up(self):
		t=time.time()
		gcode="G1 Z0 F{}".format(self.zspeed)
		t=1
		
		self.send_bloc(gcode)
		self.z=0
		self.time_movingz+=(time.time()-t)
		
	def set_tilt(self, x_tilt=0, y_tilt=0):
		self.tilt_map["x_tilt"] = x_tilt
		self.tilt_map["y_tilt"] = y_tilt
	
	def measure_tilt(self, start_x, start_y, up_x, up_y):
		self.up()
		self.set_tilt()
		self.gotoxy( x_pos = start_x, y_pos = start_y)
		z_start = self.probe_z()
		self.gotoxy( x_pos = start_x + up_x, y_pos = start_y)
		z_xvar = self.probe_z()
		self.gotoxy( x_pos = start_x, y_pos = start_y + up_y)
		z_yvar = self.probe_z()
		
		delta_zx = z_xvar - z_start
		delta_zy = z_yvar - z_start
		
		x_tilt = (delta_zx + 0.0)/(up_x + 0.0)
		y_tilt = (delta_zy + 0.0)/(up_y + 0.0)
		
		print("x_tilt = " + str(x_tilt))
		print("y_tilt = " + str(y_tilt))
		
		self.set_tilt(x_tilt, y_tilt)
		self.tilt_map_og[0] = start_x
		self.tilt_map_og[1] = start_y
		
	def measure_tilt_3p(self, point1, point2, point3):
		#point1 is taken as the origin 
		if point1 == point2 or point1 == point3 or point2 == point3: raise ValueError("measure_tilt_3p requires 3 different points")
		delta_x2 = point2[0] - point1[0]
		delta_x3 = point3[0] - point1[0]
		delta_y2 = point2[1] - point1[1]
		delta_y3 = point3[1] - point1[1]
		
		collinear = False
		if delta_x2 == 0 and delta_x3 == 0: collinear = True
		elif delta_y2 == 0 and delta_y3 == 0: collinear = True
		else:
			if delta_y2 != 0 and delta_y3 != 0:
				if (delta_x2 + 0.0)/(delta_y2 + 0.0) == (delta_x3 + 0.0)/(delta_y3 + 0.0): collinear = True
		
		if collinear: raise ValueError("measure_tilt_3p requires 3 noncollinear points")
		
		self.up()
		self.set_tilt()
		self.gotoxy(position=point1)
		z_1 = self.probe_z()
		self.gotoxy(position=point2)
		z_2 = self.probe_z()
		self.gotoxy(position=point3)
		z_3 = self.probe_z()
		
		delta_z2 = z_2 - z_1 
		delta_z3 = z_3 - z_1
		
		#delta_z2 = x_tilt*delta_x2 + y_tilt*delta_y2
		#delta_z3 = x_tilt*delta_x3 + y_tilt*delta_y3
		
		if delta_x2 == 0:
			y_tilt = (delta_z2 + 0.0)/(delta_y2 + 0.0)
			x_tilt = (delta_y3*delta_z2 - delta_y2*delta_z3 + 0.0)/( -delta_x3*delta_y2 + 0.0)
		elif delta_y2 == 0:
			x_tilt = (delta_z2 + 0.0)/(delta_x2 + 0.0)
			y_tilt = (delta_x2*delta_z3 - delta_x2*delta_z3 + 0.0)/( -delta_x2*delta_y3 + 0.0)
		else:
			x_tilt = (delta_y3*delta_z2 - delta_y2*delta_z3 + 0.0)/(delta_x2*delta_y3 - delta_x3*delta_y2 + 0.0)
			y_tilt = (delta_x2*delta_z3 - delta_x2*delta_z3 + 0.0)/(delta_x3*delta_y2 - delta_x2*delta_y3 + 0.0)
		
		print("x_tilt = " + str(x_tilt))
		print("y_tilt = " + str(y_tilt))
		
		self.set_tilt(x_tilt, y_tilt)
		self.tilt_map_og[0] = point1[0]
		self.tilt_map_og[1] = point1[1]			
	
	def gotoxy(self, x_pos=None,y_pos=None, speed=None, position=None, do_tilt=False):
		if position is None:
			x = x_pos
			y = y_pos
		else:
			x = position[0]
			y = position[1]
		delta_x = x - self.x
		delta_y = y - self.y
		if do_tilt:
			z = self.z + delta_x*self.tilt_map["x_tilt"] + delta_y*self.tilt_map["y_tilt"]
		else:
			z = self.z
		z = max( z, 0)
		self.gotoxyz( x_pos=x, y_pos=y, z_pos=z, speed=speed)
	
	def gotoxyz(self, x_pos=None,y_pos=None, z_pos=None, speed=None, position=None):
		if x_pos is None and y_pos and position is None:
			raise IOError("gcode_handler.gotoxy() can not have both (x_pos, y_pos and z_pos) and position arguments set as None")
		t=time.time()
		x = x_pos
		y = y_pos
		z = z_pos
		if speed is None:
			move_speed = self.speed
		else:
			move_speed = speed
		if position is not None:
			x = position[0]
			y = position[1]
			z = position[2]
		distance=sqrt((self.x-x)**2+(self.y-y)**2)
		gcode="G1 X{} Y{} Z{} F{}".format(x,y,z,move_speed)
		self.send_bloc(gcode)
		self.x=x
		self.y=y
		self.z=z
		self.time_movingxy+=(time.time()-t)		
	
	def set_pressure(self, press, glue_delay=0.1, no_flush=True):
		p_gcode = "M3 S{}".format(press)
		if not self.is_glueing:
			if no_flush:
				self.glue_thread = Thread(target=self.wait_empty_queue)
				self.glue_thread.setDaemon(True)
				self.glue_thread.start()
			
				self.serial_p.timeout = self.time_out_short
			
				
			
				self.flush_off()
			#else:
			self.glue_start = time.time()
			self.is_glueing = True
			self.send_bloc(p_gcode)
			self.wait(glue_delay)
		else:
			self.send_bloc(p_gcode)
			
	def stop_pressure(self, glue_delay=0.1):
		if self.is_glueing:
			self.time_glueing += (time.time() - self.glue_start)
			self.is_glueing = False
			
			self.wait(glue_delay)
			self.send_bloc("M5")
			if not self.do_flush:
				self.flush_on()
				self.glue_thread.join()
			self.serial_p.timeout = self.time_out
		else:
			self.send_bloc("M5")
				
	def glue(self, turns=1):
		t=time.time()
		self.alpha=self.alpha+360.0*turns
		gcode="G0 A{0} F{1}; {2} turns".format(self.alpha,self.aspeed, turns)
		self.send_bloc(gcode)
		self.time_glueing+=(time.time()-t)
	
	def init_code(self):
		#send initialisation sequence $st=0 $jv=3 $ee=1 $ej=0
		print("initialize configuration and position")
		code="""$ex=1
		$ej=0
		$ec=0
		$ee=1
		$jv=3
		$js=1
		$sv=2 ; stsat rep 2
		; PWM config for glue dispenser
		$p1frq=10000 ;10kHz
		$p1csl=0     ;lowest=0
		$p1csh=5700 ; highest in mbar
		$p1cpl=0.0
		$p1cph=1.0 ;for 1.0 duty cycle
		$p1pof=0.0 ;set m5 (off pressure) to 0
		;M3 S<speed> to use
		;
		G61 ;e-xact path model
		G21; select mm unit (just in case)
		G40 ; cancel cutter radius compensation
		G28.2 Z0 ;
		G28.2 Y0 ;
		G28.2 X0 ;
		G1 Z0 F1000 ;move Z to high position
		"""
		#G28.2 X0 Y0 Z0 A0 ;homing sequence
		#G1 X300 Y250 F10000; move to paper page
		self.send_bloc(code, no_wait=False)
		print("initialized")
	
	def home(self):
		bloc = """
		G28.2 Z0 ;
		G28.2 Y0 ;
		G28.2 X0 ;
		"""
		self.send_bloc(bloc)
	
	def closing_code(self):
		code="""
		M5; stop the glueing
		G1 Z10 F1000 ;move Z to high position
		G1 X300 Y250 F10000; move to paper page
		"""
		self.send_bloc(code)
		
	def emergency_stop(self, signal, frame):
		self.kill = True
		print("killed")
		time.sleep(1)
		unsuccesfull = True
		while unsuccesfull:
			try:
				self.send_line("M0")
				self.send_line("G1 Z0 F1000")
				self.send_line("M30")
				self.send_line("$qf")
				unsuccesfull = False
			except Exception as ex:
				print(ex)
				unsuccesfull = True
		response = self.serialport_pnp.readline()
		print(response)
		print("Emergency stop occured")
		exit(0)
		
	def wait(self, wait_time, sleep=False):
		w_gcode = "G4 P{}".format(wait_time)
		self.send_bloc(w_gcode)
		if sleep: time.sleep(wait_time)
		
	def close(self):
		print("This is the end")
		self.send_bloc("M30")
		print("Turn away and count to ten")
	
	def __del__(self):
		print("This is the end")
		self.send_bloc("M30")
		print("Turn away and count to ten")
		
		
class drawing():
	"""
	Drawings stored in dxf files using boarders layer, glue_lines layer, glue_zigzag layer, glue_dots layer and glue_drops layer
	not all these layers need to be there
	"""
	def __init__(self, dxf_file_name, offset=MIN_OFFSET, hight=BOARDS_CFG['hight_1'], line_speed=None, line_pressure=None, speed_dict=None, pressure_dict=None):
		# Loading file
		if line_speed is None and speed_dict is None: raise ValueError("Translation dict needed for speed line widths")
		if line_pressure is None and pressure_dict is None: raise ValueError("Translation dict needed for pressure line colors")
		self.file_name = dxf_file_name
		self.hight = hight
		print("loading data from " + dxf_file_name)
		dwg=ezdxf.readfile(dxf_file_name)
		mod=dwg.modelspace()
		
		self.offset = offset

		# Declare and fill variables from the file
		self.drawing = {}
		self.drawing["boarders"] = []
		self.drawing["glue_dots"] = []
		self.drawing["glue_lines"] = []
		self.drawing["glue_lines_s"] = []
		self.drawing["glue_lines_p"] = []
		self.drawing["glue_zigzag"] = []
		self.drawing["glue_zigzag_s"] = []
		self.drawing["glue_zigzag_p"] = []
		self.drawing["glue_drops"] = []
		for e in mod:
			if e.dxftype() == 'LINE' and e.dxf.layer=="border":
				self.drawing["boarders"].append([e.dxf.start, e.dxf.end])
			if e.dxftype() == 'LINE' and e.dxf.layer=="glue_lines":
				self.drawing["glue_lines"].append([e.dxf.start, e.dxf.end])
				if line_speed is None:
					#print( "Speed cal: read width", e.dxf.lineweight, "out of dict ", speed_dict[e.dxf.lineweight])
					self.drawing["glue_lines_s"].append(speed_dict[e.dxf.lineweight])
				else:
					self.drawing["glue_lines_s"].append(line_speed)
				if line_pressure is None:
					#print( "Pressure cal: read width", e.dxf.color, "out of dict ", pressure_dict[e.dxf.color])
					self.drawing["glue_lines_p"].append(pressure_dict[e.dxf.color])
				else:
					self.drawing["glue_lines_p"].append(line_pressure)
				
			if e.dxftype() == 'LINE' and e.dxf.layer=="glue_zigzag":
				self.drawing["glue_zigzag"].append([e.dxf.start, e.dxf.end])
				if line_speed is None:
					self.drawing["glue_zigzag_s"].append(speed_dict[e.dxf.lineweight])
				else:
					self.drawing["glue_zigzag_s"].append(line_speed)
				if line_pressure is None:
					self.drawing["glue_zigzag_p"].append(pressure_dict[e.dxf.color])
				else:
					self.drawing["glue_zigzag_p"].append(line_pressure)
			
			if e.dxftype() == 'POINT' and e.dxf.layer=="glue_dots":
				if e.dxf.location not in self.drawing["glue_dots"]: self.drawing["glue_dots"].append(e.dxf.location)
			
			if e.dxftype() == 'CIRCLE' and e.dxf.layer=="glue_drops":
				#print("circle found", e.dxf.keys())
				self.drawing["glue_drops"].append(e.dxf.center)
			#print(e.dxftype(), e.dxf.layer)
			
	def draw_lines(self, machine, key="boarders", set_pen=False):
		
		# Check input config
		hight = self.hight
		lines = self.drawing[key]
		try:
			lines_w = self.drawing[key + "_s"]
		except KeyError:
			lines_w = None
		try:
			pressue_v = self.drawing[key + "_p"]
		except KeyError:
			pressue_v = None
		offset = self.offset
		offset_test(offset)
		if lines_w is not None and len(lines) != len(lines_w): raise IOError("draw_lines: lines and lines_w must have same length")
		if pressue_v is not None and len(lines) != len(pressue_v): raise IOError("draw_lines: lines and pressue_v must have same length")
		if len(lines) == 0: 
			print("draw_lines: no lines found.")
			return
		
		# Set machine positions
		init_move=lines[0][0]
		machine.gotoxy(init_move[0] + offset[0], init_move[1] + offset[1])
		previous_point=lines[0][0]
		machine.down(hight)
		if set_pen:
			raw_input("-set pen")

		# Draw the lines
		for i,l in enumerate(lines):
			startpoint=l[0]
			endpoint=l[1]
			if startpoint!=previous_point:
				machine.stop_pressure()
				machine.up()
				machine.gotoxy(startpoint[0] + offset[0], startpoint[1] + offset[1])
				machine.down(hight)
			#goto end point
			if pressue_v is not None: machine.set_pressure(pressue_v[i])
			if lines_w is None:
				machine.gotoxy(endpoint[0] + offset[0], endpoint[1] + offset[1])
			else:
				machine.gotoxy(endpoint[0] + offset[0], endpoint[1] + offset[1], lines_w[i])
			previous_point=endpoint
		machine.stop_pressure()
		machine.up()
		
	def draw_dots(self, machine, set_pen=False):
		hight = self.hight
		offset = self.offset
		try:
			dots = self.drawing["glue_dots"]
		except KeyError:
			raise IOError("No glue_dots found in " + self.file_name)
		offset_test(offset)
		machine.up()
		machine.gotoxy(dots[0][0] + offset[0], dots[0][1] + offset[1])
	
		if set_pen:
			machine.down(hight)
			raw_input("-set pen")
		n=0
		for p in dots:
			n+=1
			#print "{0:06.1f}\t {2}/{3} {1}".format(-start+time.time(),p,n,len(glue_dots))
			machine.up()
			machine.gotoxy(p[0] + offset[0], p[1] + offset[1])
			machine.down(hight)
			machine.glue(1)
			machine.up()
	
	def drop_glue(self, machine, drop_time, pressure, index=0):
		if "glue_drops" not in self.drawing or len(self.drawing["glue_drops"]) == 0: raise ValueError("Attempted to drop glue, while no drop points found")
		print("glue_drops", self.drawing["glue_drops"])
		drop_point = self.drawing["glue_drops"][index]
		offset = self.offset
		machine.gotoxy(drop_point[0] + offset[0], drop_point[1] + offset[1])
		#machine.down(proper_hight)
		machine.set_pressure(pressure, no_flush=False)
		time.sleep(drop_time)
		machine.stop_pressure()
		#machine.up()
	
	def draw(self, machine, boarders=False, lines=True, zigzag=True, dots=False):

		# Draw the borders (to be removed)
		#answer = raw_input("Do you want to draw the borders? (y/n) ")
		#if answer == "y":
		if boarders:
			print "-drawing borders"
			self.draw_lines( machine, set_pen=True)

		# Glue the lines
		if not self.drawing["glue_lines"] == []:
			#answer = raw_input("Do you want to draw glue lines? (y/n) ")
			if lines:
				print "-gluing lines"
				self.draw_lines(machine, key="glue_lines", set_pen=True)
		if not self.drawing["glue_zigzag"] == []:
			#answer = raw_input("Do you want to draw glue zigzags? (y/n) ")
			if zigzag:
				print "-gluing zigzag"
				self.draw_lines(machine, key="glue_zigzag")
		if not self.drawing["glue_dots"] == []:
			#answer = raw_input("Do you want to draw glue dots? (y/n) ")
			if dots:
				print "-gluing dots"
				self.draw_dots(machine)
			
def offset_test(offset):
	
	# Test if offset will not be out of range
	if offset[0] < MIN_OFFSET[0]: raise ValueError("DANGER: x offset to low, nozzle will collide with rack.")
	if offset[1] < MIN_OFFSET[1]: print("WARNING: y offset lower then MIN_OFFSET[y], may draw out of range.")
	
	
	