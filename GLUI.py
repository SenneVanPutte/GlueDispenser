import sys
import ezdxf
import json
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from glueing_cfg import DRAWING_CFG, JIG_CFG, GRID_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord_grid, make_quick_func, drawing2, calc_bend, make_jig_tilt_grid
from scale_handler import scale_handler, delay_and_flow_regulation, read_glue_type, load_f_and_p, write_f_and_p, measure_flow_GUI

TABLE_HIGHT = 42.
GLUE_LIST = ['None', 'PT601', 'SY186','WATER']
SCALE_POSITION = [350, 200]
MAX_PRESSURE = 5600.
MIN_PRESSURE = 65.

DEFAULT_DRAWING      = 'kapton'
DEFAULT_JIG          = 'kapton_B'
DEFAULT_GRID         = '1x1'
DEFAULT_POS_CAL_IDX  = 'all'
DEFAULT_TILT_CAL_IDX = 'all'
DEFAULT_GLUE         = GLUE_LIST[0]
DEFAULT_GLUE_CT      = None
DEFAULT_FLOW         = 0.3
DEFAULT_PRESSURE     = 0.

class GLUI(QtGui.QWidget):

	def __init__(self, parent=None):
		super(GLUI, self).__init__(parent)
		self.setGeometry(50, 50, 1000, 700)
		self.setWindowTitle("GLUI")
		
		self.machine = None
		#self.machine.init_code()
		#self.scale = scale_handler()
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		#self.main_window
		#self.flow_window
		#self.position_cal_wondow
		
		# Drawing drop down
		self.current_drawing = DEFAULT_DRAWING
		draw_dd = QtGui.QComboBox()
		for drawing in DRAWING_CFG:
			draw_dd.addItem(drawing)
		draw_dd.setCurrentIndex(DRAWING_CFG.keys().index(DEFAULT_DRAWING))
		draw_dd.activated[str].connect(self.choose_drawing)
		self.grid.addWidget(draw_dd, 4, 1)
		draw_lb = QtGui.QLabel('Selected Drawing:')
		self.grid.addWidget(draw_lb, 4, 0)
		
		# Jig drop down
		self.current_jig = DEFAULT_JIG
		jig_dd = QtGui.QComboBox()
		for jig in JIG_CFG:
			jig_dd.addItem(jig)
		jig_dd.setCurrentIndex(JIG_CFG.keys().index(DEFAULT_JIG))
		jig_dd.activated[str].connect(self.choose_jig)
		self.grid.addWidget(jig_dd, 5, 1)
		jig_lb = QtGui.QLabel('Selected Jig:')
		self.grid.addWidget(jig_lb, 5, 0)
		
		# Grid drop down
		self.current_grid = DEFAULT_GRID
		grid_dd = QtGui.QComboBox()
		for grid in GRID_CFG:
			grid_dd.addItem(grid)
		grid_dd.setCurrentIndex(GRID_CFG.keys().index(DEFAULT_GRID))
		grid_dd.activated[str].connect(self.choose_grid)
		self.grid.addWidget(grid_dd, 6, 1)
		grid_lb = QtGui.QLabel('Selected Grid:')
		self.grid.addWidget(grid_lb, 6, 0)
		
		# Overview plot
		self.figure_ov, self.figure_ov_ax = plt.subplots() 
		#self.figure_ov = plt.figure(figsize=(10,5))
		self.canvas_ov = Canvas(self.figure_ov)
		self.grid.addWidget(self.canvas_ov, 0, 0, 4, 2)
		self.plot_ov()
		
		
		# Calibrate position button and drop down
		self.pos_cal_idx = DEFAULT_POS_CAL_IDX
		self.pos_cal_idx_dd = QtGui.QComboBox()
		self.load_dd_pos_cal() 
		self.pos_cal_idx_dd.activated[str].connect(self.choose_pos_cal_idx)
		self.grid.addWidget(self.pos_cal_idx_dd, 0, 3)
		
		position_cal_btn = QtGui.QPushButton('Calibrate')
		position_cal_btn.clicked.connect(self.pos_cal)
		self.grid.addWidget(position_cal_btn, 0, 4)
		position_cal_lb = QtGui.QLabel('Calibrate position:')
		self.grid.addWidget(position_cal_lb, 0, 2)
		
		# Calibrate tilt button and drop down
		self.tilt_speed = 25
		self.pos_func_dict = None
		self.load_pos_func_dict()
		self.tilt_cal_idx = DEFAULT_TILT_CAL_IDX
		self.tilt_cal_idx_dd = QtGui.QComboBox()
		self.load_dd_tilt_cal() 
		self.tilt_cal_idx_dd.activated[str].connect(self.choose_tilt_cal_idx)
		self.grid.addWidget(self.tilt_cal_idx_dd, 1, 3)
		
		tilt_cal_btn = QtGui.QPushButton('Calibrate')
		tilt_cal_btn.clicked.connect(self.tilt_cal)
		self.grid.addWidget(tilt_cal_btn, 1, 4)
		tilt_cal_lb = QtGui.QLabel('Calibrate tilt:')
		self.grid.addWidget(tilt_cal_lb, 1, 2)
		
		# Glue selector
		self.scale = None
		q_list = ['Select Glue Type:', 'Glue Ceartion Time:']
		t_list = ['glue', 'time']
		self.glue_sel_a = [DEFAULT_GLUE, DEFAULT_GLUE_CT]
		self.current_glue = DEFAULT_GLUE
		self.current_glue_ct = DEFAULT_GLUE_CT
		self.current_flow = DEFAULT_FLOW
		self.current_pressure = DEFAULT_PRESSURE
		
		self.glue_window = q_box(
							q_list, 
							t_list, 
							self, 
							'glue_sel_a', 
							exit_functions=['load_glue_sel']
							)
		
		glue_set_btn = QtGui.QPushButton('Set Glue')
		glue_set_btn.clicked.connect(self.set_glue)
		self.grid.addWidget(glue_set_btn, 2, 2)
		
		self.glue_label = QtGui.QLabel('')
		self.load_glue_sel()
		self.grid.addWidget(self.glue_label, 2, 3, 1, 2)
		
		# Calibrate flow
		flow_cal_btn = QtGui.QPushButton('Calibrate')
		flow_cal_btn.clicked.connect(self.flow_cal)
		self.grid.addWidget(flow_cal_btn, 3, 4)
		position_cal_lb = QtGui.QLabel('Calibrate flow:')
		self.grid.addWidget(position_cal_lb, 3, 2)
		
		
		
		
		# Init machine button
		machine_init_btn = QtGui.QPushButton('Init')
		machine_init_btn.clicked.connect(self.init_machine)
		self.grid.addWidget(machine_init_btn, 7, 4)
		machine_init_lb = QtGui.QLabel('Init LitePlacer:')
		self.grid.addWidget(machine_init_lb, 7, 2)
		
		
		
		self.show()
		#self.machine.init_code()
		
	def choose_drawing(self, text):
		self.current_drawing = str(text)
		self.plot_ov()
		#print(self.current_drawing)
		
	def choose_jig(self, text):
		self.current_jig = str(text)
		self.plot_ov()
		self.load_pos_func_dict()
		self.load_dd_tilt_cal()
		#print(self.current_jig)
		
	def choose_grid(self, text):
		self.current_grid = str(text)
		self.plot_ov()
		self.load_dd_pos_cal()
		self.load_pos_func_dict()
		self.load_dd_tilt_cal()
		#print(self.current_grid)
		
	def choose_pos_cal_idx(self, text):
		if 'all' in str(text):
			self.pos_cal_idx = str(text)
		else:
			self.pos_cal_idx = int(str(text))
		print(self.pos_cal_idx)
		
	def choose_tilt_cal_idx(self, text):
		if 'all' in str(text):
			self.tilt_cal_idx = str(text)
		else:
			self.tilt_cal_idx = int(str(text))
		print(self.tilt_cal_idx)
		
	def dxf_to_xy(self, dxf_file, layer):
		dwg = ezdxf.readfile(dxf_file)
		mod = dwg.modelspace()
		
		x_points = []
		y_points = []
		for e in mod:
			#if not layer in e.dxf.layer: continue
			if layer != e.dxf.layer: continue
			#layer = e.dxf.layer
			dxf_type = e.dxftype()
			if dxf_type == 'LINE': 
				x_points.append([e.dxf.start[0], e.dxf.end[0]])
				y_points.append([e.dxf.start[1], e.dxf.end[1]])

		return x_points, y_points
		
	def plot_ov(self):
		plt.cla()
		style = 'b'
		#ax = self.figure_ov.add_subplot(111)
		ax = self.figure_ov_ax
		x_l, y_l = self.dxf_to_xy(
							DRAWING_CFG[self.current_drawing]['file'], 
							DRAWING_CFG[self.current_drawing]['layer']
							)
		
		for jig in GRID_CFG[self.current_grid]:
			if not isinstance(jig, int): continue
			
			total_offset_x = GRID_CFG[self.current_grid][jig][0] 
			total_offset_x += JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][0] 
			total_offset_x += JIG_CFG[self.current_jig]['offsets']['drawing_position'][0]
			
			total_offset_y = GRID_CFG[self.current_grid][jig][1] 
			total_offset_y += JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][1] 
			total_offset_y += JIG_CFG[self.current_jig]['offsets']['drawing_position'][1]
			
			plt.text(
					total_offset_x, 
					total_offset_y, 
					str(jig), 
					ha='right',
					va='top',
					)
			
			for idx in range(len(x_l)):
				x_temp = [x + total_offset_x for x in x_l[idx]]
				y_temp = [y + total_offset_y for y in y_l[idx]]
				ax.plot(x_temp, y_temp, style)
		ax.set_xlim([0, 400])
		ax.set_ylim([0, 400])
		self.canvas_ov.draw()
			
	def pos_cal(self):
	
		file_name = 'cache/CooFile_'+self.current_jig+'_'+self.current_grid+'.py'
		
		ret_code = make_jig_coord_grid(
						self.machine, 
						JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][0], 
						JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][1], 
						up=15, 
						dx=JIG_CFG[self.current_jig]['probe']['dx'], 
						dy=JIG_CFG[self.current_jig]['probe']['dy'], 
						dth=JIG_CFG[self.current_jig]['probe']['dth'], 
						probe_x=JIG_CFG[self.current_jig]['probe']['probe_x'], 
						probe_y=JIG_CFG[self.current_jig]['probe']['probe_y'], 
						cache_file=file_name,
						grid_dict=GRID_CFG[self.current_grid], 
						grid_idx=self.pos_cal_idx,
						)
	
	def tilt_cal(self):
		file_name = 'cache/CooFile_'+self.current_jig+'_'+self.current_grid+'.py'
		max_hight = TABLE_HIGHT - JIG_CFG[self.current_jig]['offsets']['jig_hight'] - JIG_CFG[self.current_jig]['tilt']['max_height']
		
		ret_code = make_jig_tilt_grid(
					self.machine, 
					JIG_CFG[self.current_jig]['tilt']['p1'], 
					JIG_CFG[self.current_jig]['tilt']['p2'],  
					JIG_CFG[self.current_jig]['tilt']['p3'],  
					max_hight, 
					self.tilt_speed, 
					coord_func_dict=self.pos_func_dict, 
					cache_file=file_name, 
					grid_dict=GRID_CFG[self.current_grid], 
					grid_idx=self.tilt_cal_idx
					)
			
	def load_dd_pos_cal(self):
		self.pos_cal_idx_dd.clear()
		
		cb_items = ['all']
		for idx in GRID_CFG[self.current_grid]:
			if not isinstance(idx, int): continue
			cb_items.append(str(idx))
		cb_items.sort()
		for idx in range(len(cb_items)):
			self.pos_cal_idx_dd.addItem(cb_items[idx])
		
		self.pos_cal_idx = DEFAULT_POS_CAL_IDX
		def_idx = cb_items.index(str(DEFAULT_POS_CAL_IDX))
		self.pos_cal_idx_dd.setCurrentIndex(def_idx)
			
	def load_dd_tilt_cal(self):
		self.tilt_cal_idx_dd.clear()
		
		cb_items = ['all']
		for idx in GRID_CFG[self.current_grid]:
			if not isinstance(idx, int): continue
			cb_items.append(str(idx))
		cb_items.sort()
		include_all = True
		for idx in range(len(cb_items)):
			self.tilt_cal_idx_dd.addItem(cb_items[idx])
			if not 'all' in cb_items[idx]:
				if self.pos_func_dict[int(cb_items[idx])] is None:
					include_all = False
					j = self.tilt_cal_idx_dd.model().index(idx,0)
					self.tilt_cal_idx_dd.model().setData(j, QtCore.QVariant(0), QtCore.Qt.UserRole-1)

		if not include_all:
			idx = cb_items.index('all')
			j = self.tilt_cal_idx_dd.model().index(idx,0)
			self.tilt_cal_idx_dd.model().setData(j, QtCore.QVariant(0), QtCore.Qt.UserRole-1)
		
		self.tilt_cal_idx = DEFAULT_TILT_CAL_IDX
		def_idx = cb_items.index(str(DEFAULT_TILT_CAL_IDX))
		self.tilt_cal_idx_dd.setCurrentIndex(def_idx)
		
	def load_pos_func_dict(self):
		file_name = 'cache/CooFile_'+self.current_jig+'_'+self.current_grid+'.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
		except:
			read_data = {}
		
		func_dict = {}
		for jig in GRID_CFG[self.current_grid]:
			if not isinstance(jig, int): continue
			if unicode(jig) in read_data and not read_data[unicode(jig)]['sin'] is None:
				func_dict[jig] = make_quick_func( 
									sin=read_data[unicode(jig)]['sin'], 
									cos=read_data[unicode(jig)]['cos'], 
									a=read_data[unicode(jig)]['offset_x'], 
									b=read_data[unicode(jig)]['offset_y']
									)
			else: func_dict[jig] = None
		
		self.pos_func_dict = func_dict
		
	def init_machine(self):
		try:
			self.machine = gcode_handler()
		except:
			print('Machine not made')
			pass
		self.machine.init_code()
	
	def set_glue(self):
		self.glue_window.show()
		
	def load_glue_sel(self):
		self.current_glue = self.glue_sel_a[0]
		if isinstance(self.glue_sel_a[1], str):
			split_time = self.glue_sel_a[1].split(':')
			tot_time = int(split_time[0])*60 + int(split_time[1])
			self.current_glue_ct = tot_time
		else: self.current_glue_ct = None
		
		self.glue_label.setText('Current glue: ' + self.glue_sel_a[0])
		self.new_glue_to_log()
		print(self.glue_sel_a)
		print(self.current_glue, self.current_glue_ct)
	
	def new_glue_to_log(self):
		if self.scale is None: 
			print('new_glue_to_log called but self.scale is None')
			return
		glue_cr_time = '00:00'
		if isinstance(self.glue_sel_a[1], str): glue_cr_time = self.glue_sel_a[1]
		self.scale.flow_log_new_glue(self.glue_sel_a[0], glue_cr_time)
	
	def load_flow_and_pres(self):
		file_name = 'cache/FlowFile.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
		except:
			read_data = {}
		
		for key in read_data:
			if self.current_glue in key: return read_data[key]['flow'], read_data[key]['pressure']
				
		return DEFAULT_FLOW, DEFAULT_PRESSURE
			
	def write_flow_and_pres(self):
		file_name = 'cache/FlowFile.py'
		
		try:
			ff_file = open(file_name, 'r')
			read_data = json.load(func_file)
			ff_file.close()
		except:
			read_data = {}
			
		new_data = copy.deepcopy(read_data)
		new_data[self.current_glue] = {'flow': self.current_flow, 'pressure': self.current_pressure}
		
		ff_file = open(file_name, 'w')
		ff_file.write(json.dumps(new_data, indent=2))
		ff_file.close()
		
	def flow_cal(self):
		self.flow_window = fit_window(self)
		if self.scale is None:
			self.scale = scale_handler(False)
			self.new_glue_to_log()
		
		self.flow_window.show()
		
		# pressure, delay, measured_flow = delay_and_flow_regulation(
												# machiene, 
												# scale, 
												# scale_pos,  
												# init_pressure, 
												# DRAWING_CFG[layer]['desired_flow'], 
												# precision=DRAWING_CFG[layer]['flow_precision'], 
												# mass_limit=mass_lim, 
												# threshold=20, 
												# show_data=True, 
												# init=True
												# )
		#init_pressure => load previous, if None take initial guess drawing, else recalculate on desired flow
		#mass_limit glue dependent
		
		#show data: 
		# - after each iteration show new window with fit
		# - two buttons: good or bad fit
		#  - if bad: popup to ask if redo is needed
		#  - if good: re-iterate if needed
		
	
	#def draw
	#set tilt_map and tilt_map_og for every jig!!!

class q_box(QtGui.QWidget):

	def __init__(self, q_list, t_list, main_window, attr_name, exit_functions=[], pix_w=500, pix_h=200, parent=None):
		print('init q_box')
		super(q_box, self).__init__(parent)
		self.setGeometry(50, 50, pix_w, pix_h)
		self.main_window = main_window
		self.attr_name = attr_name
		self.exit_functions = exit_functions
		
		self.q_list = q_list
		self.t_list = t_list
		self.a_list = []
		self.w_dict = {}
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		# Add question boxes
		for idx in range(len(self.q_list)):
			lb_w = QtGui.QLabel(q_list[idx])
			self.grid.addWidget(lb_w, idx, 0)
			self.input_w(idx)
			
		# Add submit box
		submit_btn = QtGui.QPushButton('Submit')
		submit_btn.clicked.connect(self.submit)
		self.grid.addWidget(submit_btn, len(self.q_list), 4)
				
	def input_w(self, idx):
		if self.t_list[idx] == 'time':
			
			w1 = QtGui.QLabel('hour:')
			w2 = QtGui.QSpinBox()
			w3 = QtGui.QLabel('min :')
			w4 = QtGui.QSpinBox()
			
			w1.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
			w3.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
			
			w2.setMaximum(23)
			w4.setMaximum(59)
			
			self.grid.addWidget(w1, idx, 1)
			self.grid.addWidget(w2, idx, 2)
			self.grid.addWidget(w3, idx, 3)
			self.grid.addWidget(w4, idx, 4)
			
			self.w_dict[idx] = [w1, w2, w3, w4]
			
		elif self.t_list[idx] == 'glue':
			w = QtGui.QComboBox()
			
			for glue in GLUE_LIST:
				w.addItem(glue)
			w.setCurrentIndex(0)
			self.grid.addWidget(w, idx, 1, 1, 4)
			
			self.w_dict[idx] = w
		
		else:
			w = QtGui.QLineEdit()
			
			self.grid.addWidget(w, idx, 1, 1, 4)
			
			self.w_dict[idx] = w
	
	def output_a(self, idx):
		if self.t_list[idx] == 'time':
			h = int(self.w_dict[idx][1].value())
			m = int(self.w_dict[idx][3].value())
			return str(h).zfill(2)+':'+str(m).zfill(2)
			
		elif self.t_list[idx] == 'glue':
			return str(self.w_dict[idx].currentText())
			
		else:
			return str(self.w_dict[idx].text())
	
	def collect_answers(self):
		a_list = []
		for idx in range(len(self.q_list)):
			a_list.append(self.output_a(idx))
		self.a_list = a_list
	
	def submit(self):
		print('submited')
		self.collect_answers()
		setattr(self.main_window, self.attr_name, self.a_list)
		for func_str in self.exit_functions:
			func = getattr(self.main_window, func_str)
			func()
		self.close()
			
class fit_window(QtGui.QWidget):

	def __init__(self, main_window, guess_pressure=False, pix_w=700, pix_h=500, parent=None):
		
		super(fit_window, self).__init__(parent)
		
		self.setGeometry(50, 50, pix_w, pix_h)
		self.main_window = main_window
		self.desired_flow = DRAWING_CFG[main_window.current_drawing]['desired_flow']
		self.flow_precision = DRAWING_CFG[main_window.current_drawing]['flow_precision']
		if guess_pressure:
			self.set_pressure(main_window.current_pressure)
			self.guess_pressure(main_window.current_flow)
		else:
			self.set_pressure = DRAWING_CFG[main_window.current_drawing]['init_pressure']
		self.max_factor = 5.
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		self.figure, self.figure_ax = plt.subplots() 
		#self.figure_ov = plt.figure(figsize=(10,5))
		self.canvas = Canvas(self.figure)
		self.grid.addWidget(self.canvas, 0, 0, 1, 3)
		#self.canvas.draw()
		
		self.progress_bar = QtGui.QProgressBar()
		self.grid.addWidget(self.progress_bar, 1, 0, 1, 3)
		
		# Start button 
		self.start_btn = QtGui.QPushButton('Start')
		self.start_btn.clicked.connect(self.start)
		self.start_btn.setEnabled(True)
		self.grid.addWidget(self.start_btn, 2, 0)
		
		# Good fit/ Bad fit buttons
		self.good_btn = QtGui.QPushButton('Good')
		self.good_btn.clicked.connect(self.good)
		self.good_btn.setEnabled(False)
		self.grid.addWidget(self.good_btn, 2, 1)
		self.bad_btn = QtGui.QPushButton('Bad')
		self.bad_btn.clicked.connect(self.bad)
		self.bad_btn.setEnabled(False)
		self.grid.addWidget(self.bad_btn, 2, 2)
		
		
	def move_to_scale(self):
		self.main_window.machine.gotoxy(position=SCALE_POSITION)
		self.main_window.machine.down(7)
		scale_height = self.main_window.machine.probe_z(speed=50)[2]
		needle_height = scale_height - 1
		
	def start(self):
		self.start_btn.setEnabled(False)
		self.move_to_scale()
		self.flow_iteration()	
		
	def flow_iteration(self):
		self.main_window.scale.zero()
		mass_lim = 150
		if self.main_window.current_glue == 'SY186': mass_lim = 250
		if self.main_window.current_glue == 'WATER': mass_lim = 500
		time_out = max((mass_limit + 50 + 0.)/((self.desired_flow + 0.)/2.), 100)
		
		#plt.cla()
		self.figure_ax.clear()
		
		flow = measure_flow_GUI(
				elf.main_window.machine, 
				self.main_window.scale, 
				self.set_pressure, 
				3, # second to wait before and after
				mass_lim, 
				20, 
				self.figure_ax, 
				self.progress_bar, 
				time_out=30
				)
		self.measured_flow = flow
		
		self.canvas.draw()
		self.good_btn.setEnabled(True)
		self.bad_btn.setEnabled(True)
	
	def good(self):
		self.good_btn.setEnabled(False)
		self.bad_btn.setEnabled(False)
		
		if abs(self.measured_flow - self.desired_flow) < self.flow_precision:
			self.main_window.current_flow = self.measured_flow
			self.main_window.current_pressure = self.set_pressure
			self.close_window()
		else:
			self.guess_pressure(self.measured_flow)
			self.flow_iteration()
	
	def bad(self):
		self.good_btn.setEnabled(False)
		self.bad_btn.setEnabled(False)
		choise = QtGui.QMessageBox(
						self, 
						'Redo Fit?', 
						'Do you want to redo the flow calibration with the current settings?',
						QtGui.QMessageBox.Yes | QtGui.QMessageBox.No
						)
		if choise == QtGui.QMessageBox.Yes:
			self.flow_iteration()
		else:
			self.close_window()
	
	def guess_pressure(self, flow):
		factor_tmp = self.desired_flow/max(flow+0., 0.01)
		factor = min(max(factor_tmp, 1./self.max_factor),self.max_factor)
		pressure_tmp = factor*self.set_pressure
		self.set_pressure = max(min(MAX_PRESSURE, pressure_tmp), MIN_PRESSURE)
	
	def close_window(self):
		self.main_window.machine.up()
		self.close()
			
			
		
		
		
		
		
			
			
	# initial needs:
	#machiene.gotoxy(position=pos)
	#machiene.down(7)
	#scale_height = machiene.probe_z(speed=50)[2]
	#needle_height = scale_height - 1
	#if init: scale.zero()
	
	#machiene.down(needle_height, do_tilt=False) 
			
		
	
		
	

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	GUI = GLUI()
	sys.exit(app.exec_())
	