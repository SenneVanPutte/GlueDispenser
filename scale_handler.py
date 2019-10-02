import io
import serial
import time
import matplotlib
from matplotlib import pyplot
import numpy
import Queue
from threading import Thread
import datetime

class scale_handler():
	"""
	connection to the calibration scale
	"""
	def __init__(self):
		ser = serial.Serial(r"COM4", baudrate=1000000, xonxoff=False, timeout=0)
		self.clear_time = 0.3
		# Sample rate in sec
		self.read_freq = 0.1
		self.time_out = 0.3
		self.n_avg = None
		self.serial_p = ser
		self.serialport_pnp = io.TextIOWrapper(io.BufferedRWPair(ser, ser, buffer_size=65536), newline='\n')
		self.conf_avg()
		self.record_file="scale_log.txt" 
		record_file = open(self.record_file, 'a')
		record_file.write("#\t ____START_SCALE_SESSION____\n")
		record_file.write("#\t TIME: " + datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S") + "\n")
		record_file.close()
		
		
	def send_command(self, command):
		self.serial_p.write(command)
	
	def zero(self):
		self.send_command("t")
		self.clear_buffer()
		time.sleep(0.01)
		self.clear_buffer()
	
	def calibrate(self, option="g", clear_time=None):
		'''
		g = 5.8g
		h = 50g
		'''
		mass_str = 'Xg'
		if option == "g": mass_str = '5.8g' 
		elif option == "h": mass_str = '50g' 
		raw_input("Put " + mass_str+ " calibration weight on the scale")
		self.send_command(option)
		time.sleep(2)
		raw_input("Remove calibration weight")
		self.clear_buffer()
			
	def conf_avg(self, option="c"):
		'''
		a = 1 or 0.1s
		b = 5 or 0.2s
		c = 10 or 1s
		d = 40 or 4s
		e = 160 or 16s
		f = 600 or 1min
		'''
		self.send_command(option)
		if option == "a": self.n_avg = 1
		elif option == "b": self.n_avg = 5
		elif option == "c": self.n_avg = 10
		elif option == "d": self.n_avg = 40
		elif option == "e": self.n_avg = 160
		elif option == "e": self.n_avg = 600
		else: raise ValueError('Unknown avg setting')
			
	def read_port(self):
		#response = self.serialport_pnp.readline()
		response = self.serialport_pnp.readlines()
		#response = self.serial_p.readline()[:-1]
		if response != []: return response[-1]
		return ''
		
	def read_port_h(self):
		response = self.read_port()
		if response != '':
			temp = response.replace(' ', '').replace('\n', '').replace('\t', '/')
			temp = temp.split('/') 
			for i, val in enumerate(temp):
				temp[i] = float(val)
		else:
			temp = [None, None, None, None]
		return temp
	
	def read_mass(self):
		mass = None
		start_t = time.time()
		while mass is None and time.time() - start_t < self.time_out:
			mass = self.read_port_h()[1]
		if mass is None: raise ValueError('read_mass timed out')
		return mass
		
	def read_out_time(self, duration, display=True, dt_print=0.5, record=False, data=None):
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
	
	def read_out_time_if(self, duration, condition_queue, dt_print=0.5, record=True):
		condition_met = False
		while not condition_met:
			time.sleep(0.1)
			if not condition_queue.Empty:
				condition_met = True
		return self.read_out_time(duration, dt_print=dt_print, record=record)

	def clear_buffer(self):
		time.sleep(self.clear_time)
		self.read_port()
	
	def write_record(self, data):
		record_file = open(self.record_file, 'a')
		for entry in data:
			rec_str = str(entry[0]) + '\t' + str(entry[1]) + '\n' 
			record_file.write(rec_str)
		record_file.close()
			
	
	def plot_data(self, data, extra_plots=None):
		x = []
		y = []
		for entry in data:
			x.append(entry[0])
			y.append(entry[1][1])
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
				style = 'r-'
				for keyy in extra_plots:
					if key_splt[0] in keyy and '_x' in keyy: x_temp = extra_plots[keyy]
					if key_splt[0] in keyy and '_y' in keyy: y_temp = extra_plots[keyy]
					if key_splt[0] in keyy and '_style' in keyy: style = extra_plots[keyy]
				x_temp_st = 0#min(x_temp)
				x_temp_rel = [val - x_temp_st for val in x_temp]
				ax.plot(x_temp_rel, y_temp, style, label=key_splt[0])
			ax.legend()

		ax.set(xlabel='time (s)', ylabel='mass (g)', title='')
		pyplot.show()
 
def record_pressure(machiene, scale, pressure, duration, relaxation_time):
	data = []
	measure_thread = Thread(target=scale.read_out_time, args=(duration+relaxation_time,), kwargs={'record': True, 'data': data})
	measure_thread.setDaemon(True)
	measure_thread.start()
	
	machiene.set_pressure(pressure, no_flush=False)
	time.sleep(duration)
	machiene.stop_pressure()
	
	measure_thread.join()
	return data

def delay_and_flow_regulation2(machiene, scale, pos, init_pressure, desired_flow, precision=1, duration=5, threshold=20, show_data=True, init=True):
	'''
	pos in [x, y, z]
	pressure in mbar
	threshold in mg (wait for threshold to start flow measurement)
	desired flow in mg/s (750 mm/s => 17 s/board + 200 mg/board =>  11 or 12 mg/s)
	'''
	machiene.gotoxyz(position=pos)
	scale_height = machiene.probe_z(speed=25)[2]
	needle_height = scale_height - 1
	
	relaxation_time = 10
	#relaxation_time = scale.read_freq*scale.n_avg
	
	if init: scale.zero()
	
	machiene.down(needle_height) 
	
	# TODO: Start scale for duration store in data
	pressure = init_pressure
	th = (threshold + 0.)/(1000 + 0.)
	lin_fit = {}
	
	data = record_pressure(machiene, scale, pressure, duration, relaxation_time)
	#data = record_pressure(machiene, scale, pressure, duration, relaxation_time)
	delay, flow, x_sim, y_sim = calc_delay_and_flow(data, th, scale)

	lin_fit['fit_x'] = x_sim
	lin_fit['fit_y'] = y_sim

	if show_data: scale.plot_data(data, extra_plots=lin_fit)
	
	while abs(flow - desired_flow) > precision:
		scale.zero()
		print('Previous pressure: ' + str(pressure) + ' Previous flow: ' + str(flow) )
		factor = desired_flow/flow
		factor = min(max(factor, 0.1),10)
		pressure = factor*pressure
		
		data = record_pressure(machiene, scale, pressure, duration, relaxation_time)
		delay, flow, x_sim, y_sim = calc_delay_and_flow(data, th, scale)

		lin_fit['fit_x'] = x_sim
		lin_fit['fit_y'] = y_sim

		if show_data: scale.plot_data(data, extra_plots=lin_fit)
	
	return pressure, delay, flow
 
def calc_delay_and_flow(data, th, scale):
	start_t = data[0][0]
	pressur_found = False
	
	start_w = data[0][1][1]
	end_w = data[-1][1][1]
	tw_start = data[-1][0]
	tw_end = data[0][0]
	for entry in data:
		if not pressur_found and entry[1][3]: pressur_found = True
		if start_t == data[0][0] and entry[1][3]: start_t = entry[0]
		if entry[1][1] < end_w - th and entry[0] > tw_end: tw_end = entry[0]
		if entry[1][1] > start_w + th and entry[0] < tw_start: tw_start = entry[0]
		
	if tw_start > tw_end: 
		scale.plot_data(data)
		raise ValueError('Time window messed up')
	
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
	a, b = lin_reg(tw_time, tw_mass)
	print(a,b)
	
	delay = (start_w - a +0.)/(b + 0.)
	flow = b*1000

	print(flow, delay)
	
	#x_sim = [t + delay for t in tw_time]
	x_sim = tw_time
	y_sim = [t*b + a for t in tw_time]
	print(len(x_sim))
	print(len(y_sim))

	return delay, flow, x_sim, y_sim
	
		
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
		
	
def delay_and_flow_regulation(machiene, scale, pos, init_pressure, desired_flow, precision=1, duration=5, threshold=40, show_data=True):
	'''
	pos in [x, y, z]
	init_pressure in mbar
	desired flow in mg/s (750 mm/min 182 mm => 14.56 s/board + 200 mg/board =>  13.73 mg/s)
	threshold in mg (wait till x mg collected before the start of flow measurement)
	'''
	scale.zero()
	start_mass = scale.read_mass()
	start_time = time.time()
	
	delay_t, new_pressure, measured_flow, old_data = measure_delay(
		machiene, 
		scale, 
		pos, 
		init_pressure, 
		duration=duration, 
		threshold=threshold, 
		desired_flow=desired_flow, 
		init=False, 
		)
	print('Delay is '+str(delay_t)+' s' )
	if show_data: scale.plot_data(old_data)
	
	#measured_flow = 0
	prev_flow = measured_flow
	#new_pressure = init_pressure
	prev_pressure = init_pressure
	
	while abs(measured_flow - desired_flow) > precision:
	
		#machiene.down(needle_height) 
		print("New flow regulator cycle")
		print("Testing pressure: " + str(new_pressure) + " mbar" + ", Previous flow: " + str(prev_flow) + " mg/s")
	
		# TODO: Start scale for duration store in data
		data = []
		measure_thread = Thread(target=scale.read_out_time, args=(duration+2,), kwargs={'record': True, 'data': data})
		measure_thread.setDaemon(True)
		measure_thread.start()
	
		machiene.set_pressure(new_pressure, no_flush=False)
		time.sleep(duration)
		machiene.stop_pressure()
		
		measure_thread.join()
		
		init_mass = data[0][1][1]
		final_mass = data[-1][1][1]
		start_t = data[0][0]
		end_t = data[-1][0]
		
		for entry in data:
			#if start_t == data[0][0] and entry[1][3]: start_t = entry[0]
			if entry[1][3]: 
				start_t = entry[0]
				break
		for entry in data:
			if start_t + delay_t + 0.5 <= entry[0]:
				start_t = entry[0]
				break
		
		measured_flow = (final_mass-init_mass+0.0)*1000/(end_t - start_t + 0.0)
		
		print("Measured flow: " + str(measured_flow) + " mg/s, Desired flow: " + str(desired_flow) + " mg/s, Presision: " + str(precision) + " mg/s")
		
		# Calculate new pressure (version1: linear scaling with pressure assumed )
		#if new_pressure == prev_pressure:
		#	# flow = cte * pressure => pressure = flow / cte and cte = flow / pressure
		#	prev_pressure = new_pressure
		#	#cte = (measured_flow + 0.)/(prev_pressure + 0.)
		#	new_pressure = ((desired_flow + 0.)/(measured_flow + 0.))*prev_pressure
		
		if measured_flow > desired_flow:
			curr_pres = new_pressure
			if prev_pressure > new_pressure: new_pressure = new_pressure + (new_pressure - prev_pressure)
			else: new_pressure = prev_pressure - (new_pressure - prev_pressure + 0.)/2.
			prev_pressure = curr_pres
		
		elif measured_flow < desired_flow:
			curr_pres = new_pressure
			if prev_pressure < new_pressure: new_pressure = new_pressure + (new_pressure - prev_pressure)
			else: new_pressure = prev_pressure - (new_pressure - prev_pressure + 0.)/2.
			prev_pressure = curr_pres
		
		new_pressure = max(new_pressure, 0.)
		prev_flow = measured_flow
		
	end_mass = scale.read_mass()
	print('Took '+str(time.time() - start_time)+' s, and '+str((end_mass-start_mass)*1000) + ' mg') 
	machiene.up()
	return new_pressure, delay_t
	
	
def flow_test(machiene, scale, pos, pressure_list, duration=5, delay_t=0, empty_check=False):
	machiene.gotoxyz(position=pos)
	scale_height = machiene.probe_z(speed=25)[2]
	needle_height = scale_height - 1
	scale.zero()
	flow_list = []
	flow_list_up = []
	flow_list_dn = []
	
	
	for pres in pressure_list:
		if empty_check: 
			machiene.turn_lsz_off()
			raw_input('Seringe empty?')
			machiene.turn_lsz_on()
		time.sleep(2)
		print(pres)
	
		machiene.down(needle_height) 
		
		data = []
		measure_thread = Thread(target=scale.read_out_time, args=(duration+2,), kwargs={'record': True, 'data': data})
		measure_thread.setDaemon(True)
		measure_thread.start()
	
		machiene.set_pressure(pres, no_flush=False)
		time.sleep(duration)
		machiene.stop_pressure()
		
		measure_thread.join()
		
		init_mass = data[0][1][1]
		init_mass_std = data[0][1][2]
		final_mass = data[-1][1][1]
		final_mass_std = data[-1][1][2]
		start_t = data[0][0]
		end_t = data[-1][0]
		
		for entry in data:
			if start_t == data[0][0] and entry[1][3]: start_t = entry[0]
		
		measured_flow = (final_mass-init_mass+0.0)*1000/(end_t - start_t - delay_t + 0.0)
		measured_flow_up = (final_mass -init_mass+0.0 + final_mass_std + init_mass_std)*1000/(end_t - start_t - delay_t + 0.0)
		measured_flow_dn = (final_mass -init_mass+0.0 - final_mass_std - init_mass_std)*1000/(end_t - start_t - delay_t + 0.0)
		
		flow_list.append(measured_flow)
		flow_list_up.append(measured_flow_up)
		flow_list_dn.append(measured_flow_dn)
		
	return flow_list, flow_list_up, flow_list_dn
		
		
def lin_reg(x, y):
	'''
	y = a + b*x
	'''
	if len(x) != len(y): raise ValueError('lin_reg: input lists must be of same length')
	if len(x) < 2: raise ValueError('lin_reg: lists must be at least length 2')

	x_sum = 0
	y_sum = 0
	for it in range(len(x)):
		x_sum += float(x[it])
		y_sum += float(y[it])

	x_mean = x_sum/(len(x) + 0.)
	y_mean = y_sum/(len(y) + 0.)

	cov_xy = 0
	var_x = 0
	for it in range(len(x)):
		cov_xy += (float(x[it]) - x_mean)*(float(y[it]) - y_mean)
		var_x += (float(x[it]) - x_mean)**2
	
	b = cov_xy/var_x
	a = y_mean - b*x_mean
	return a, b
		
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
	
	
		