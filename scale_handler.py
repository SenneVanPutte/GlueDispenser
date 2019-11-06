import io
import serial
import time
import matplotlib
from matplotlib import pyplot
import numpy
import Queue
from threading import Thread
import datetime
import os
import time
import math
from scipy.stats import t

class scale_handler():
	"""
	connection to the calibration scale
	"""
	def __init__(self):
		ser = serial.Serial(r"COM4", baudrate=1000000, xonxoff=False, timeout=0)
		self.clear_time = 0.3
		# Sample rate in sec
		#self.read_freq = 0.125
		self.read_freq = 0.1
		self.time_out = 0.3
		self.n_avg = None
		self.relax_time = None
		self.serial_p = ser
		self.serialport_pnp = io.TextIOWrapper(io.BufferedRWPair(ser, ser, buffer_size=64*1024), newline='\n')
		
		day_str = datetime.datetime.now().strftime("%Y_%b_%d")
		self.glue_log = "glue_"+day_str+".log"
		if not os.path.isfile(self.glue_log): open(self.glue_log, 'w+')
		
		self.conf_avg()
		self.record_file="scale_"+day_str+".log"
		if not os.path.isfile(self.record_file): record_file = open(self.record_file, 'w')
		else: record_file = open(self.record_file, 'a')
		record_file.write("#\t ____START_SCALE_SESSION____\n")
		record_file.write("#\t TIME: " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")
		record_file.close()
		
		self.flow_log="flow_"+day_str+".log"
		if not os.path.isfile(self.flow_log): record_file = open(self.flow_log, 'w')
		else: record_file = open(self.flow_log, 'a')
		record_file.write("#\t ____START_FLOW_SESSION____\n")
		record_file.write("#\t TIME: " + datetime.datetime.now().strftime("%H:%M:%S") + "\n")
		record_file.close()
		
		
		
	def init_glue_log(self):
		log = open(self.glue_log, 'a+')
		log.write("#\t ____START_GLUE_SESSION____\n")
		log.write("#\t TIME: " + datetime.datetime.now().strftime("%H:%M:%S") + "\t("+str(time.time())+")" + "\n")
		log.close()
		
	def write_glue_log(self, log_str, time_stamp=False):
		log = open(self.glue_log, 'a+')
		time_str = str(time.time())
		if time_stamp: log.write(time_str + "\t" + log_str + "\n")
		else: log.write(log_str + "\n")
		log.close()
	
	def write_flow_log(self, pressure, flow, delay):
		log = open(self.flow_log, 'a+')
		time_str = str(time.time())
		log_str = 'pressure: \t' + str(pressure) + '\t flow: \t' + str(flow) + ' \t delay: \t' + str(delay) 
		log.write(time_str + "\t" + log_str + "\n")
		log.close()
		
	def send_command(self, command):
		self.write_glue_log("")
		self.write_glue_log("scale send command: " + command)
		self.write_glue_log("")
		self.serial_p.write(command)
		time.sleep(0.1)
		self.serial_p.flush()
	
	def zero(self):
		self.send_command("t t ")
		self.clear_buffer()
		time.sleep(0.1)
		#self.send_command("t")
		self.clear_buffer()
		#return
		#time.sleep(0.1)
		start = time.time()
		#print(self.read_port_h())
		#mass = self.read_port_h()[1]
		time_out = 10
		mass = self.read_mass_avg()
		
		while( abs(mass) > 0.01):
			self.send_command("t")
			time.sleep(0.2)
			mass = self.read_mass()
			if time.time() - start > time_out:	
				print("Zeroing took longer then : " + str(time_out) + "s ")
				return
		return
				# break
		
		
	
	def calibrate(self, option="g", clear_time=None):
		'''
		g = 1g
		h = 50g
		'''
		mass_str = 'Xg'
		mass_exp = 1
		if option == "g": 
			mass_str = '1 g' 
			mass_exp = 1
		elif option == "h": 
			mass_str = '50 g'
			mass_exp = 50
		raw_input("Put " + mass_str+ " calibration weight on the scale")
		self.send_command(option)
		time.sleep(2)
		
		start = time.time()
		#print(self.read_port_h())
		#mass = self.read_port_h()[1]
		time_out = 10
		mass = self.read_mass_avg()
		
		while( abs(mass - mass_exp) > 0.01):
			self.send_command(option)
			time.sleep(0.2)
			mass = self.read_mass()
			if time.time() - start > time_out:	
				print("Calibrating took longer then : " + str(time_out) + "s ")
				break
		
		
		raw_input("Remove calibration weight")
		self.clear_buffer()
		return
			
	def conf_avg(self, option="d"):
		'''
		a = 1 or 0.1s
		b = 5 or 0.2s
		c = 10 or 1s
		d = 40 or 4s
		e = 160 or 16s
		f = 600 or 1min
		'''
		self.send_command(option)
		self.write_glue_log("")
		self.write_glue_log("scale average set: " + option)
		self.write_glue_log("")
		if option == "a": self.n_avg = 1
		elif option == "b": self.n_avg = 5
		elif option == "c": self.n_avg = 10
		elif option == "d": self.n_avg = 40
		elif option == "e": self.n_avg = 160
		elif option == "e": self.n_avg = 600
		else: raise ValueError('Unknown avg setting')
		self.relax_time = self.n_avg*self.read_freq
		time.sleep(self.relax_time+1)
		#time.sleep(2)
			
	def read_port(self):
		#response = self.serialport_pnp.readline()
		response = self.serialport_pnp.readlines()
		#print(response)
		#response = self.serial_p.readline()[:-1]
		if response != []: return response[-1]
		return ''
		
	def read_port_h(self):
		"""
		[instant_value, average, sigma, pressure_on]
		"""
		response = self.read_port()
		if response != '':
			temp = response.replace(' ', '').replace('\n', '').replace('\t', '/')
			temp = temp.split('/') 
			for i, val in enumerate(temp):
				temp[i] = float(val)
			self.write_glue_log("scale read: " +str(temp[0])+", "+str(temp[1])+", "+str(temp[2])+", "+str(temp[3]), time_stamp=True)
		else:
			temp = [None, None, None, None]
		
		return temp
	
	def read_mass(self):
		mass = None
		start_t = time.time()
		while mass is None and time.time() - start_t < self.time_out:
			mass = self.read_port_h()[0]
		if mass is None: raise ValueError('read_mass timed out')
		return mass
	
	def read_mass_avg(self):
		mass = None
		start_t = time.time()
		while mass is None and time.time() - start_t < self.time_out:
			mass = self.read_port_h()[1]
		if mass is None: raise ValueError('read_mass timed out')
		return mass
		
	def read_out_time(self, duration, display=True, dt_print=0.5, record=False, data=None):
		self.clear_buffer()
		if data is None: data = [] 
		start = time.time()
		#prev_time = time.time()
		plot_th = 0
		while time.time() - start < duration:
			value = self.read_port_h()
			if value[0] is not None:
				if time.time() - start > plot_th and display:
					if value[3]: bool_str = "pressure is  ON"
					else: bool_str = "pressure is OFF"
					print '{:6.4} {:6.4} {:6.4} in {:5.3}s {}\r'.format(value[0], value[1], value[2], time.time() - start, bool_str),
					plot_th += dt_print
				#if record and time.time() - prev_time > self.read_freq/2:
				if record:
					data.append((time.time(), value))
					#prev_time = time.time()
			#if value[0] is not None: print '{:6.4} {:6.4} {:6.4} in {:4.3}s'.format(value[0], value[1], value[2], time.time() - start)
			#time.sleep(1)
		print '' 
		self.write_record(data)
		return data
	
	def set_pressure(self, machiene, pressure, cmd_queue):
		machiene.set_pressure(pressure, no_flush=False)
		#cmd_queue.get()
		#machiene.stop_pressure()
		#return
		pressure_on = True
		while pressure_on:
		
			cmd = cmd_queue.get()
			#exQueue.empty: cmd = '' 
			#print('thread got cmd: "' + str(cmd) + '"')
			if cmd == 'kill_pressure':
				machiene.stop_pressure()
				pressure_on = False
				cmd_queue.task_done()
		return 
	
	def read_out_flow(self, machiene, pressure, time_ba, mass_lim, display=True, dt_print=0.5, time_out=30):
		"""
		Read scale till 'mass_limit' in mg is accumulated on scale.
		machiene = gcode_handler object
		pressure = pressure for machiene in mbar
		time_ba  = wait time before and after in s 
		"""
		cmd_queue = Queue.Queue()
		pressure_thread = Thread(target=self.set_pressure, args=(machiene, pressure, cmd_queue))
		pressure_thread.setDaemon(True)
		
		th_mass = mass_lim/1000.
		data = []
		redo = False
		plot_th = 0
		
		waiting_befor = True
		waiting_after = True
		measuring = True
		satisfied = False
		start_b = time.time()
		start_m = None
		start_a = None
		avg_mass = None
		mass_b = []
		mass = 0.
		while not satisfied:
			value = self.read_port_h()
			
			if value[0] is not None:
				mass = value[0]
				if waiting_befor: mass_b.append(mass)
				if time.time() - start_b > plot_th and display:
					if value[3]: bool_str = "pressure is  ON"
					else: bool_str = "pressure is OFF"
					
					if waiting_befor:
						progress = 0.
						eta = time_out
					elif not waiting_befor and measuring:
						sigma = value[2]
						mean = value[1] - avg_mass + 0.
						progress = (mean + 2.*sigma)/(th_mass + 0.)
						eta = min((time.time() - start_b - time_ba)*(1./progress -1.), time_out)
					else:
						progress = 1.
						eta = 0.
					
					prc_str = '[' + '='*int(40*progress) + ' '*(40 - int(40*progress)) +']'
					progress_str = '{} [{:6.4} %]'.format(prc_str, progress*100)
					print '{} {:6.4} {:6.4} {:6.4} in {:6.4}s ETA {:6.4}s {}\r'.format(progress_str, value[0]*1000, value[1]*1000, value[2]*1000, time.time() - start_b, eta, bool_str),
					plot_th += dt_print
				
				data.append((time.time(), value))
			if waiting_befor and time.time() - start_b > time_ba:
				# Go from waiting to measuring
				avg_mass = (sum(mass_b) + 0.)/(len(mass_b) + 0.)
				#print(avg_mass)
				start_m = time.time()
				waiting_befor = False
				pressure_thread.start()
			if not waiting_befor and measuring:
				# Go from measuring to waiting after
				if mass - avg_mass > th_mass: 
					start_a = time.time()
					measuring = False
					cmd_queue.put('kill_pressure')
				elif time.time() - start_m > time_out:
					cmd_queue.put('kill_pressure')
					print('read_out_flow: timed out, mass limit of '+str(mass_lim)+'mg was not met')
					redo = True
					break
			if not measuring and waiting_after and time.time() - start_a > time_ba + 3:
				# stop
				waiting_after = False
			satisfied = not (waiting_befor or measuring or waiting_after)
		print '' 
		print('waiting for join')
		pressure_thread.join()
		
		
		self.write_record(data)
		return data, redo
		
	def read_out_flow2(self, machiene, pressure, time_ba, mass_lim, n_data=2000, display=True, dt_print=0.5, time_out=30):
		"""
		Read scale till 'mass_limit' in mg is accumulated on scale.
		machiene = gcode_handler object
		pressure = pressure for machiene in mbar
		time_ba  = wait time before and after in s 
		"""
		cmd_queue = Queue.Queue()
		pressure_thread = Thread(target=self.set_pressure, args=(machiene, pressure, cmd_queue))
		pressure_thread.setDaemon(True)
		
		th_mass = mass_lim/1000.
		data = []
		redo = False
		plot_th = 0
		
		waiting_befor = True
		waiting_after = True
		measuring = True
		satisfied = False
		start_b = time.time()
		start_m = None
		start_a = None
		avg_mass = 0.
		mass_b = []
		mass = 0.
		aq_data = 0
		while not satisfied:
			value = self.read_port_h()
			
			if value[0] is not None:
				mass = value[0]
				if not waiting_befor and measuring and value[3]: aq_data += 1
				if waiting_befor: mass_b.append(mass)
				if time.time() - start_b > plot_th and display:
					if value[3]: bool_str = "pressure is  ON"
					else: bool_str = "pressure is OFF"
					
					if measuring and not value[3]:
						progress = 0.
						eta = time_out + 0.
					elif not waiting_befor and measuring and value[3]:
						progress = (aq_data + 0.)/(n_data + 0.)
						eta = min((time.time() - start_b - time_ba)*(1./progress -1.), time_out)
					else:
						progress = 1.
						eta = 0.
					
					prc_str = '[' + '='*int(40*progress) + ' '*(40 - int(40*progress)) +']'
					progress_str = '{} [{:6.4} %]'.format(prc_str, progress*100)
					#print '{} {:6.4} {:6.4} {:6.4} in: {:6.4}s ETA: {:6.4}s {}\r'.format(progress_str, value[0]*1000, value[1]*1000, value[2]*1000, time.time() - start_b, eta, bool_str),
					print '{} glue used: {:6.4} mg, in: {:6.4}s, ETA: {:6.4}s, {}\r'.format(progress_str, (value[1] - avg_mass)*1000, time.time() - start_b, eta, bool_str),
					plot_th += dt_print
				
				data.append((time.time(), value))
			if waiting_befor and time.time() - start_b > time_ba:
				# Go from waiting to measuring
				avg_mass = (sum(mass_b) + 0.)/(len(mass_b) + 0.)
				start_m = time.time()
				waiting_befor = False
				pressure_thread.start()
			if not waiting_befor and measuring:
				# Go from measuring to waiting after
				if mass - avg_mass > th_mass or aq_data > n_data: 
					start_a = time.time()
					measuring = False
					cmd_queue.put('kill_pressure')
				elif time.time() - start_m > time_out:
					cmd_queue.put('kill_pressure')
					print('read_out_flow: timed out, mass limit of '+str(mass_lim)+'mg was not met')
					redo = True
					break
			if not measuring and waiting_after and time.time() - start_a > time_ba + 3:
				# stop
				waiting_after = False
			satisfied = not (waiting_befor or measuring or waiting_after)
		print '' 
		print('waiting for join')
		pressure_thread.join()
		
		
		self.write_record(data)
		return data, redo
	
	def read_out_time_if(self, duration, condition_queue, dt_print=0.5, record=True):
		condition_met = False
		while not condition_met:
			time.sleep(0.1)
			if not condition_queue.Empty:
				condition_met = True
		return self.read_out_time(duration, dt_print=dt_print, record=record)

	def clear_buffer(self):
		"""
		read_port() reads all the lines and only returns the last one
		"""
		time.sleep(self.clear_time)
		self.read_port()
	
	def write_record(self, data):
		record_file = open(self.record_file, 'a')
		for entry in data:
			rec_str = str(entry[0]) + '\t' + str(entry[1]) + '\n' 
			record_file.write(rec_str)
		record_file.close()
			
	
	def plot_data(self, data, extra_plots=None, text=None):
		x = []
		y = []
		for entry in data:
			x.append(entry[0])
			y.append(entry[1][0])
		x_st = min(x)
		x_rel = [val - x_st for val in x]
		fig, ax = pyplot.subplots() 
		ax.plot(x_rel, y, label='measurement')

		# Plot extra's 
		if not extra_plots is None:
			for key in extra_plots:
				if not '_x' in key: continue
				key_splt = key.split('_')
				x_temp = []
				y_temp = []
				style = 'r'
				for keyy in extra_plots:
					keyy_splt = keyy.split('_')
					if key_splt[0] == keyy_splt[0] and '_x' in keyy: x_temp = extra_plots[keyy]
					if key_splt[0] == keyy_splt[0] and '_y' in keyy: y_temp = extra_plots[keyy]
					if key_splt[0] == keyy_splt[0] and '_style' in keyy: style = extra_plots[keyy]
				x_temp_st = 0#min(x_temp)
				x_temp_rel = [val - x_temp_st for val in x_temp]
				ax.plot(x_temp_rel, y_temp, style, label=key_splt[0])
			ax.legend(loc='lower right')
		
		if not text is None:
		    #right = min(x)+ (max(x) - min(y))*0.75
			#bottom = min(y) + (max(y) - min(y))*0.25
			left = 0.01
			right = 0.99
			top = 0.98
			bottom = 0.01
			pyplot.text(left, top, text, horizontalalignment='left', verticalalignment='top', transform=ax.transAxes )

		ax.set(xlabel='time (s)', ylabel='mass (g)', title='')
		pyplot.show()
 
def record_pressure(machiene, scale, pressure, duration, wait_time):
	data = []
	measure_thread = Thread(target=scale.read_out_time, args=(duration+4*wait_time,), kwargs={'record': True, 'data': data})
	measure_thread.setDaemon(True)
	measure_thread.start()
	
	time.sleep(wait_time)
	machiene.set_pressure(pressure, no_flush=False)
	time.sleep(duration)
	machiene.stop_pressure()
	
	measure_thread.join()
	return data
	
def measure_flow(machiene, scale, pressure, wait_time, mass_lim, mass_threshold, show_data=True, time_out=30, low_flow=False):

	mass_th = mass_threshold/1000.

	max_retry = 1
	attempt = 0
	redo = True
	delay = 0
	flow = 0
	flow_int = [-9999, 9999]
	x_sim = []
	y_sim = []
	y_sim_up = []
	y_sim_dn = []
	
	while redo and attempt < max_retry:
		attempt += 1
		if low_flow: data, redo = scale.read_out_flow2(machiene, pressure, wait_time, mass_lim, display=True, dt_print=0.5, time_out=time_out)
		else: data, redo = scale.read_out_flow(machiene, pressure, wait_time, mass_lim, display=True, dt_print=0.5, time_out=time_out)
		if not redo:
			ret_dict = calc_delay_and_flow(data, mass_th, scale, wait_time, low_flow)
			delay = ret_dict['delay']
			flow = ret_dict['flow']
			flow_int = ret_dict['flow_int']
			x_sim = ret_dict['x_sim']
			y_sim = ret_dict['y_sim']
			y_sim_up = ret_dict['y_sim_up']
			y_sim_dn = ret_dict['y_sim_dn']
			redo = ret_dict['redo']
			x_st = ret_dict['x_st']
			x_fi = ret_dict['x_fi']
			y_st = ret_dict['y_st']
		if not redo and show_data:
			lin_fit = {}
			lin_fit['Fit_x'] = x_sim
			lin_fit['Fit_y'] = y_sim
			lin_fit['Fit_style'] = 'r'
			lin_fit['Fit Up_x'] = x_sim
			lin_fit['Fit Up_y'] = y_sim_up
			lin_fit['Fit Up_style'] = 'y--'
			lin_fit['Fit Down_x'] = x_sim
			lin_fit['Fit Down_y'] = y_sim_dn
			lin_fit['Fit Down_style'] = 'y--'
			if not x_st[0] is None:
				lin_fit['Pressure ON_x'] = x_st
				lin_fit['Pressure ON_y'] = y_st
				lin_fit['Pressure ON_style'] = 'c--'
				lin_fit['Pressure OFF_x'] = x_fi
				lin_fit['Pressure OFF_y'] = y_st
				lin_fit['Pressure OFF_style'] = 'c--'
			
			fit_text = '{:.1f} mg/s \n{:.1f} mbar'.format(flow, pressure)

			scale.plot_data(data, extra_plots=lin_fit, text=fit_text)
			scale.write_flow_log(pressure, flow, delay)
		elif show_data:
			scale.plot_data(data)
	#if redo and attempt >= max_retry: raise ValueError('measure_flow failed after ' + str(max_retry)+ ' attempts wit pressure ' + str(pressure) + 'mbar, mass threshold ' + str(mass_threshold) + 'g and duration ' + str(duration)+'s')
	if redo and attempt >= max_retry: print('measure_flow failed after ' + str(max_retry)+ ' attempts wit pressure ' + str(pressure) + 'mbar, mass threshold ' + str(mass_threshold) + 'g and time out ' + str(time_out)+'s')
	return data, delay, flow, flow_int, x_sim, y_sim, y_sim_up, y_sim_dn, redo

def delay_and_flow_regulation(machiene, scale, pos, init_pressure, desired_flow, precision=1, mass_limit=200, threshold=20, show_data=True, init=True, low_flow=True):
	'''
	pos in [x, y, z]
	pressure in mbar
	mass_limit is the mass that accumulates in mg per flow measurement 
	threshold in mg (wait for threshold to start flow measurement)
	desired flow in mg/s (750 mm/s => 17 s/board + 200 mg/board =>  11 or 12 mg/s)
	'''

	machiene.gotoxy(position=pos)
	scale_height = machiene.probe_z(speed=25)[2]
	needle_height = scale_height - 1
	
	n_samples = 30
	relaxation_time = n_samples*scale.read_freq
	#relaxation_time = scale.read_freq*scale.n_avg
	
	time_out = (mass_limit + 50 + 0.)/((desired_flow + 0.)/2.)
	print('Time out: ' + str(time_out) + ' s')
	#time_out = 120.
	
	if init: scale.zero()
	
	machiene.down(needle_height, do_tilt=False) 
	
	# TODO: Start scale for duration store in data
	pressure = init_pressure
	th = threshold 
	
	def meas_f(machiene, scale, pressure, relaxation_time, mass_limit, th, show_data=show_data, time_out=time_out):
		print('Using pressure: ' + str(pressure))
		redo = True
		attempt = 0
		max_attempts = 2
		while redo:
			attempt +=1
			if attempt > max_attempts: raise ValueError('Flow measurement failed after ' + str(max_attempts) + ' attempts' )
			data, delay, flow, flow_int, x_sim, y_sim, y_sim_up, y_sim_dn, redo = measure_flow(machiene, scale, pressure, relaxation_time, mass_limit, th, show_data=show_data, time_out=time_out, low_flow=low_flow)
			if redo:
				print('Flow measurement failed.')
				if pressure < 65:
					raise ValueError('Pressure to low. Smaller needle?')
				elif (desired_flow + 0.)*time_out < mass_limit:
					time_out = (mass_limit + 0.)/(desired_flow + 0.) + 5.
					print('time out time adjusted: '+str(time_out) + 's')
				else: 
					print('Assuming pressure to low adding 500 mbar')
					meas_f(machiene, scale, pressure + 500, relaxation_time, mass_limit, th, show_data=show_data, time_out=time_out)
				#else: raise ValueError('Flow measurement failed for unknown reason')
		return data, delay, flow, flow_int, x_sim, y_sim, y_sim_up, y_sim_dn
		
	data, delay, flow, flow_int, x_sim, y_sim, y_sim_up, y_sim_dn = meas_f(machiene, scale, pressure, relaxation_time, mass_limit, th, show_data=show_data)
	prev_press = pressure
	while abs(flow - desired_flow) > precision:
		scale.zero()
		print('Previous pressure: ' + str(pressure) + ' Previous flow: ' + str(flow) )
		factor_tmp = desired_flow/max(flow, 0.01)
		factor = min(max(factor_tmp, 0.2),5)
		pressure_tmp = factor*pressure
		pressure = max(min(5600, pressure_tmp), 65)
		if pressure == prev_press: print('limit reached?')
		
		prev_press = pressure
		data, delay, flow, flow_int, x_sim, y_sim, y_sim_up, y_sim_dn = meas_f(machiene, scale, pressure, relaxation_time, mass_limit, th, show_data=show_data)
	
	return pressure, delay, flow
 
def calc_delay_and_flow(data, th, scale, relax_time, low_flow):
	t_pres_on = None
	t_pres_of = None
	start_t = data[0][0]
	end_t = data[-1][0]
	befor_mass = []
	after_mass = []
	b_mass = 0
	a_mass = 0
	x_tot = []
	y_tot = []
	for point in data:
		cur_time = point[0]
		cur_mass = point[1][0]
		pres_bit = point[1][-1]
		x_tot.append(cur_time)
		y_tot.append(cur_mass)
		
		# Fixing mass window before and after
		if cur_time < start_t + relax_time: 
			befor_mass.append(cur_mass)
			b_mass += cur_mass
		if cur_time > end_t - relax_time: 
			after_mass.append(cur_mass)
			a_mass += cur_mass
		
		# Pressure times
		if t_pres_on is None and pres_bit:
			t_pres_on = cur_time 
		if not t_pres_on is None:
			if t_pres_of is None and not pres_bit:
				t_pres_of = cur_time 
	
	b_mass /= len(befor_mass)
	a_mass /= len(after_mass)
	
	#print('avergage mass before: ' + str(b_mass) )
	#print('avergage mass after: ' + str(a_mass) )
	
	pressur_found = False
	redo = False
	
	start_w = data[0][1][0]
	end_w = data[-1][1][0]
	tw_start = start_t + relax_time
	tw_end = end_t - relax_time
	#print('th hier is '+ str(th))
	
	went_below = True
	went_above = False
	#searching = False
	#prev_mass = None
	for entry in data:
		cur_time = entry[0]
		cur_mass = entry[1][0]
		if cur_time < start_t + relax_time or cur_time > end_t - relax_time: continue
		# if not pressur_found and entry[1][3]: pressur_found = True
		# if start_t == data[0][0] and entry[1][3]: start_t = cur_time
		# if cur_mass < a_mass - th and cur_time > tw_end: tw_end = cur_time
		# if cur_mass > b_mass + th and cur_time < tw_start: tw_start = cur_time
		
		
		if cur_mass < b_mass + th: went_below = True
		if cur_mass > b_mass + th and went_below:
			went_below = False
			searching = True
			tw_start = cur_time
			#prev_mass = cur_mass
		#if searching:
			#if prev_mass
			#prev_mass = cur_mass
	
		if cur_mass > a_mass - th and not went_above: 
			went_above = True
			tw_end = cur_time
		#if cur_mass <
			
		
		if cur_mass < b_mass + th and cur_time < tw_start: tw_start = cur_time
	
	if not t_pres_of is None: tw_end = t_pres_of
	if low_flow and not t_pres_on is None:
		tw_start = t_pres_on + 10.
		tw_end = t_pres_of
	if tw_start > tw_end: 
		scale.plot_data(data)
		#raise ValueError('Time window messed up')
		print('Time window messed up')
		redo = True
		return 9999, 9999, [], [], [], [], [], redo
	
	tw_mass = []
	tw_time = []
	
	for entry in data:
		if entry[0] > tw_start  and entry[0] < tw_end:
			tw_mass.append(entry[1][0])
			tw_time.append(entry[0] - data[0][0])
			
	#numpy stuff
	tw_mass_np = numpy.array(tw_mass).T
	tw_time_np = numpy.array(tw_time).T
	TW_TIME = numpy.vstack([tw_time_np, numpy.ones(len(tw_time_np))]).T
	#a, b = numpy.linalg.lstsq(TW_TIME, tw_mass_np, rcond=None)[0]
	#a, b = numpy.linalg.lstsq(TW_TIME, tw_mass_np)[0]
	a_tmp, b_tmp, a_int, b_int, redo = lin_reg(tw_time, tw_mass)
	if redo: return 9999, 9999, [], [], [], [], [], redo
	#print(a_tmp, b_tmp, a_int, b_int)
	
	extra_time = (th+0.)/(b_tmp + 0.)
	if low_flow and not t_pres_on is None: extra_time = 0.
	#print('Extra time: '+ str(extra_time) )
	tw_mass_l = []
	tw_time_l = []
	tw_st_new = tw_start - extra_time
	tw_fi_new = tw_end + extra_time
	if not t_pres_on is None: tw_st_new = max(tw_start - extra_time, t_pres_on)
	if not t_pres_of is None: tw_fi_new = min(tw_end + extra_time, t_pres_of)
	for entry in data:
		if entry[0] > tw_st_new and entry[0] < tw_fi_new:
			tw_mass_l.append(entry[1][0])
			tw_time_l.append(entry[0] - data[0][0])
	a, b, a_int, b_int, redo = lin_reg(tw_time_l, tw_mass_l)
	#print(a, b, a_int, b_int)
	
	if t_pres_on is None:
		delay = (start_w - a +0.)/(b + 0.) - relax_time
	else:
		delay_tmp = (start_w - a +0.)/(b + 0.) - (t_pres_on - start_t)
		delay = max(delay_tmp, (t_pres_on - start_t) - relax_time)
	#print('Wait time: ' + str(relax_time) + ', Pressure on time: ' + str(t_pres_on - start_t) )
	flow = b*1000
	flow_int = [b_int[0]*1000, b_int[1]*1000]

	print(flow, delay)
	
	press_int = [t_pres_on - start_t, t_pres_of - start_t]
	
	
	#x_sim = [t + delay for t in tw_time]
	x_sim = [tw_time_l[0], tw_time_l[-1]]
	y_sim = [t*b + a for t in x_sim]
	y_st = [tw_time_l[0]*b_int[1] + a_int[1], 
		tw_time_l[0]*b_int[1] + a_int[0], 
		tw_time_l[0]*b_int[0] + a_int[1], 
		tw_time_l[0]*b_int[0] + a_int[0]]
	y_nd = [tw_time_l[-1]*b_int[1] + a_int[1], 
		tw_time_l[-1]*b_int[1] + a_int[0], 
		tw_time_l[-1]*b_int[0] + a_int[1], 
		tw_time_l[-1]*b_int[0] + a_int[0]]
	y_sim_up = [max(y_st), max(y_nd)]
	y_sim_dn = [min(y_st), min(y_nd)]
	#print(len(x_sim))
	#print(len(y_sim))
	
	x_st = [t_pres_on - start_t, t_pres_on - start_t]
	x_fi = [t_pres_of - start_t, t_pres_of - start_t]
	y_st = [min(y_tot), max(y_tot)]
	
	return_dict = {}
	return_dict['delay'] = delay
	return_dict['flow'] = flow
	return_dict['flow_int'] = flow_int
	return_dict['x_sim'] = x_sim
	return_dict['y_sim'] = y_sim
	return_dict['y_sim_up'] = y_sim_up
	return_dict['y_sim_dn'] = y_sim_dn
	return_dict['redo'] = redo
	return_dict['press_int'] = press_int
	return_dict['x_st'] = x_st
	return_dict['x_fi'] = x_fi
	return_dict['y_st'] = y_st

	return return_dict
	
		
def measure_delay(machiene, scale, pos, pressure, duration=5, threshold=60, desired_flow=None, init=True, show_data=False):
	'''
	pos in [x, y, z]
	pressure in mbar
	threshold in mg (wait for threshold to start flow measurement)
	desired flow in mg/s (750 mm/s => 17 s/board + 200 mg/board =>  11 or 12 mg/s)
	'''
	machiene.gotoxyz(position=pos)
	scale_height = machiene.probe_z(speed=25)[2]
	needle_height = scale_height - 1
	
	if init: scale.zero()
	
	machiene.down(needle_height) 
	
	# TODO: Start scale for duration store in data
	data = []
	measure_thread = Thread(target=scale.read_out_time, args=(duration+2,), kwargs={'record': True, 'data': data})
	measure_thread.setDaemon(True)
	measure_thread.start()
	
	machiene.set_pressure(pressure, no_flush=False)
	time.sleep(duration)
	machiene.stop_pressure()
	
	measure_thread.join()
	#machiene.up()
	
	start_w = data[0][1][1]
	start_t = data[0][0]
	end_t = data[-1][0]
	delay_t = data[-1][0]
	delay_t_up = data[-1][0]
	delay_t_dn = data[-1][0]
	th = (threshold + 0.)/(1000 + 0.)
	th_up = th + data[0][1][2]
	th_dn = th - data[0][1][2]
	final_mass = data[-1][1][1]
	delay_mass = data[0][1][1]
	pressur_found = False
	
	# Asymptotic average delay correction time ( delay = time_step*(n_avg - 1 / 2)) 
	avg_corr = scale.read_freq*(scale.n_avg -1.)/2.
	
	for entry in data:
		if not pressur_found and entry[1][3]: pressur_found = True
		if start_t == data[0][0] and entry[1][3]: start_t = entry[0]
		if entry[1][1] > start_w + th and entry[0] < delay_t: 
			delay_t = entry[0]
			delay_mass = entry[1][1]
		if entry[1][1] > start_w + th_up and entry[0] < delay_t_up: delay_t_up = entry[0]
		if entry[1][1] > start_w + th_dn and entry[0] < delay_t_dn: delay_t_dn = entry[0]
	#print('start time ', start_t-data[0][0])
	#print('delay time ', delay_t-data[0][0])
	if not pressur_found: 
		print("Delay measurement failed, no pressure found")
		return None, None, None, data
	if delay_t == data[-1][0]: 
		print("Delay measurement failed, increase duration or lower threshold")
		return None, None, None, data
		
	flow_estimate = (final_mass - delay_mass + 0.0)/(end_t - delay_t + 0.0)
	flow_estimate_mg = flow_estimate*1000
	
	delay_estimate = delay_t - ((delay_mass - start_w + 0.)/(flow_estimate))
	#if delay_estimate
	pressure_guess = None
	if desired_flow is not None: pressure_guess = ((desired_flow + 0.)/(flow_estimate_mg + 0.))*pressure
	if show_data: scale.plot_data(data)
	return max(delay_estimate - start_t - avg_corr, 0), pressure_guess, flow_estimate_mg, data
				
def flow_test(machiene, scale, pos, pressure_list, mass_lim=100, delay_t=0, empty_check=False, show_data=True):
	machiene.gotoxyz(position=pos)
	scale_height = machiene.probe_z(speed=25, up_rel=1)[2]
	needle_height = scale_height - 1
	print('needle height:' +str(needle_height))
	scale.zero()
	flow_list = []
	delay_list = []
	flow_list_up = []
	flow_list_dn = []
	
	n_samples = 30
	wait_time = n_samples*scale.read_freq
	mass_threshold = 20.
	
	
	for pres in pressure_list:
		if empty_check: 
			machiene.turn_lsz_off()
			raw_input('Seringe empty?')
			machiene.turn_lsz_on()
		time.sleep(2)
		print(pres)
	
		machiene.down(needle_height) 
		
		data, delay, flow, flow_int, x_sim, y_sim, y_sim_up, y_sim_dn, redo = measure_flow(machiene, scale, pres, wait_time, mass_lim, mass_threshold)
		
		measured_flow = flow
		measured_flow_up = flow_int[1]
		measured_flow_dn = flow_int[0]
		
		flow_list.append(measured_flow)
		flow_list_up.append(measured_flow_up)
		flow_list_dn.append(measured_flow_dn)
		
		delay_list.append(delay)
		
	return flow_list, flow_list_up, flow_list_dn, delay_list
		
		
def lin_reg(x, y, alpha=0.95):
	'''
	y = a + b*x
	'''
	if len(x) != len(y): raise ValueError('lin_reg: input lists must be of same length')
	if len(x) < 3: 
		print('lin_reg: lists must be at least length 3')
		return 9999, 9999, [], [], True
		
	
	n = len(x)
	Sx = 0.
	Sy = 0.
	Sxx = 0.
	Sxy = 0.
	Syy = 0.
	for it in range(len(x)):
		Sx += float(x[it])
		Sy += float(y[it])
		Sxx += float(x[it])*float(x[it])
		Sxy += float(x[it])*float(y[it])
		Syy += float(y[it])*float(y[it])
	
	b = (n*Sxy - Sx*Sy + 0.)/(n*Sxx - Sx*Sx + 0.)
	a = (1./(n + 0.))*Sy - b*(1./(n + 0.))*Sx
	s_e_2 = (1./(n*(n-2) +0.))*(n*Syy - Sy*Sy - b*b*(n*Sxx - Sx*Sx))
	s_b_2 = n*s_e_2/(n*Sxx + Sx*Sx)
	s_a_2 = s_b_2*s_b_2*(1./(n + 0.))*Sxx
	
	s_b = math.sqrt(s_b_2)
	s_a = math.sqrt(s_a_2)
	
	b_int = list(t.interval(alpha, n-2, b, s_b))
	a_int = list(t.interval(alpha, n-2, a, s_a))
	t_val = t.interval(alpha, n-2, 0, 1)[1]
	#print('fit param: n=' +str(n) + ', a=' + str(a) + ', s_a=' +str(s_a) + ', b=' + str(b) + ', s_b=' + str(s_b) + 't_val=' + str(t_val))
	
	return a, b, a_int, b_int, False
	
		
if __name__ == "__main__":
	scale = scale_handler()
	scale.clear_buffer()
	
	m_1=scale.read_out_time(10, record=True)
	scale.zero(0)
	m_2=scale.read_out_time(10, record=True)
	scale.zero(0)
	m_3=scale.read_out_time(10, record=True)
	
	raw_input("put ref")
	scale.send_command("g")
	m_4 = scale.read_out_time(10, record=True)
	
	raw_input("take ref")
	m_5 = scale.read_out_time(20, record=True)
	
	scale.zero(0)
	m_6=scale.read_out_time(10, record=True)
	scale.plot_data(m_1+m_2+m_3+m_4+m_5+m_6)
	scale.plot_data(m_5+m_6)
	#print read
	#raw_input("put ref")
	#scale.send_command("g")
	#scale.read_out_time(50)
	exit()
	
	
		