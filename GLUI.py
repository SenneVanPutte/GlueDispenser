# -*- coding: utf-8 -*-
import os
import cv2
import sys
import time
import ezdxf
import json
import copy
import datetime
import traceback
from threading import Thread
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
import glueing_cfg
from glueing_cfg import DRAWING_CFG, JIG_CFG, GRID_CFG, sum_offsets
from gcode_handler import gcode_handler, drawing, make_jig_coord_grid_laser, make_quick_func, drawing2, calc_bend, make_jig_tilt_grid_laser
from scale_handler import scale_handler, delay_and_flow_regulation, read_glue_type, load_f_and_p, write_f_and_p, measure_flow_GUI, timestr_to_ts, ts_to_timestr, calc_delay_and_flow
from scale_handler import calc_flow, mean, StdDev

from gcode_handler import LitePlacerError
from scale_handler import ScaleError
from tests.GLUITest import Test
from tests.TestClass import TestClass

from LaserSensor import LaserSensor

TABLE_HIGHT = 42.
GLUE_LIST = ['None', 'PT601', 'SY186','WATER', 'TestGlue']
TEST_LIST = [TestClass]
SCALE_POSITION = [350, 200]
PARK_POSITION = [450, 300]
LASER_CAL_POSITION_X = [5, 77] # Aluminum bar; [-7, 95] Kapton jig
LASER_CAL_POSITION_Y = [5, 77] # Aluminum bar; [15, 85] Kapton jig
MAX_PRESSURE = 2350. #5600.
MIN_PRESSURE = 25 #65.

DEFAULT_DRAWING      = 'kapton'
DEFAULT_JIG          = 'kapton_jig'
DEFAULT_GRID         = '1x1'
DEFAULT_POS_CAL_IDX  = 'all'
DEFAULT_TILT_CAL_IDX = 'all'
DEFAULT_GLUE         = GLUE_LIST[0]
DEFAULT_GLUE_CT      = None
DEFAULT_FLOW         = 0.3
DEFAULT_PRESSURE     = 0.
DEFAULT_BEND         = 'NeedleBendVar_blue_metal.txt'

PALETTE = QtGui.QPalette()
PALETTE.setColor(QtGui.QPalette.Background, QtCore.Qt.white)

class GLUI(QtGui.QWidget):

	def __init__(self, app, parent=None):
		start_time = time.time()
		super(GLUI, self).__init__(parent)
		self.app = app
		self.setGeometry(50, 50, 1000, 600)
		self.setWindowTitle("GLUI")
		self.setWindowIcon(QtGui.QIcon('images/GLUI_logo.png'))
		self.setPalette(PALETTE)
		
		self.thread_pool = QtCore.QThreadPool()
		self.current_bend_file = DEFAULT_BEND
		
		self.machine = None
		self.scale = None
		self.laser_sensor = None
		self.webcam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		# Menu bar
		self.menu_bar = QtGui.QMenuBar(self) #self.menuBar()
		self.load_menu()
		self.test_window = test_window(self)
		self.insp_window = inspect_window(self)
		self.scale_window = scale_window(self)
		self.grid.addWidget(self.menu_bar, 0, 0)
		
		row_offset = 1
	
		# Drawing drop down
		self.current_drawing = DEFAULT_DRAWING
		self.draw_dd = QtGui.QComboBox()
		self.load_dd_draw()
		self.draw_dd.activated[str].connect(self.choose_drawing)
		self.grid.addWidget(self.draw_dd, 8 + row_offset, 1)
		self.draw_lb = QtGui.QLabel('Selected Drawing:')
		self.grid.addWidget(self.draw_lb, 8 + row_offset, 0)
		
		# Jig drop down
		self.current_jig = DEFAULT_JIG
		self.jig_dd = QtGui.QComboBox()
		self.load_dd_jig()
		self.jig_dd.activated[str].connect(self.choose_jig)
		self.grid.addWidget(self.jig_dd, 9 + row_offset, 1)
		self.jig_lb = QtGui.QLabel('Selected Jig:')
		self.grid.addWidget(self.jig_lb, 9 + row_offset, 0)
		
		# Grid drop down
		self.current_grid = DEFAULT_GRID
		self.grid_dd = QtGui.QComboBox()
		self.load_dd_grid()
		self.grid_dd.activated[str].connect(self.choose_grid)
		self.grid.addWidget(self.grid_dd, 10 + row_offset, 1)
		self.grid_lb = QtGui.QLabel('Selected Grid:')
		self.grid.addWidget(self.grid_lb, 10 + row_offset, 0)
		
		self.load_last_setup()
		
		# Reload cfg's
		self.cfg_btn = QtGui.QPushButton('Reload')
		self.cfg_btn.clicked.connect(
									lambda: self.launch_worker(
										self.reload_cfg, 
										closing_func=[
											self.load_dd_draw,
											self.load_dd_grid,
											self.load_dd_jig,
											]
										)
									)
		self.grid.addWidget(self.cfg_btn, 11 + row_offset, 1)
		self.cfg_lb = QtGui.QLabel('Reload the configuration files:')
		self.grid.addWidget(self.cfg_lb, 11 + row_offset, 0)
		
		# Overview plot
		self.figure_ov, self.figure_ov_ax = plt.subplots() 
		#self.figure_ov = plt.figure(figsize=(10,5))
		self.canvas_ov = Canvas(self.figure_ov)
		self.grid.addWidget(self.canvas_ov, 0 + row_offset, 0, 8, 2)
		self.plot_ov()
		
		# Calibrate Laser sensor
		self.load_laser_sensor()
		self.load_last_laser_cal()
		self.laser_cal_lb = QtGui.QLabel('Calibrate laser sensor:')
		self.laser_cal_btn = QtGui.QPushButton('Calibrate')
		self.laser_cal_btn.clicked.connect(
										lambda: self.launch_worker(
											self.laser_cal, 
											check_func = [
												self.init_warning
												],
											#closing_func=[
											#	self.load_dd_tilt_cal
											#	]
											)
										)
		self.grid.addWidget(self.laser_cal_btn, 1 + row_offset, 4)
		self.grid.addWidget(self.laser_cal_lb, 1 + row_offset, 2)
		
		
		
		# Calibrate position button and drop down
		self.pos_cal_idx = DEFAULT_POS_CAL_IDX
		self.pos_cal_idx_dd = QtGui.QComboBox()
		self.load_dd_pos_cal() 
		self.pos_cal_idx_dd.activated[str].connect(self.choose_pos_cal_idx)
		self.grid.addWidget(self.pos_cal_idx_dd, 2 + row_offset, 3)
		
		self.position_cal_btn = QtGui.QPushButton('Calibrate')
		#self.position_cal_btn.clicked.connect(self.pos_cal)
		self.position_cal_btn.clicked.connect(
										lambda: self.launch_worker(
											self.pos_cal, 
											check_func = [
												self.init_warning
												],
											closing_func=[
												self.load_dd_tilt_cal
												]
											)
										)
		self.grid.addWidget(self.position_cal_btn, 2 + row_offset, 4)
		self.position_cal_lb = QtGui.QLabel('Calibrate position:')
		self.grid.addWidget(self.position_cal_lb, 2 + row_offset, 2)
		
		# Calibrate tilt button and drop down
		self.tilt_speed = 25
		self.pos_func_dict = None
		self.load_pos_func_dict()
		self.tilt_cal_idx = DEFAULT_TILT_CAL_IDX
		self.tilt_cal_idx_dd = QtGui.QComboBox()
		self.load_dd_tilt_cal() 
		self.tilt_cal_idx_dd.activated[str].connect(self.choose_tilt_cal_idx)
		self.grid.addWidget(self.tilt_cal_idx_dd, 3 + row_offset, 3)
		self.load_tilt_dict()
		
		self.tilt_cal_btn = QtGui.QPushButton('Calibrate')
		#self.tilt_cal_btn.clicked.connect(self.tilt_cal)
		self.tilt_cal_btn.clicked.connect(
									lambda: self.launch_worker(
										self.tilt_cal,
										check_func = [
											self.init_warning,
											self.coo_dict_warning,
											],
										)
									)
		self.grid.addWidget(self.tilt_cal_btn, 3 + row_offset, 4)
		self.tilt_cal_lb = QtGui.QLabel('Calibrate tilt:')
		self.grid.addWidget(self.tilt_cal_lb, 3 + row_offset, 2)
		
		# Glue selector
		self.scale = None
		q_list = ['Select Glue Type:', 'Glue Creation Time:']
		t_list = ['glue', 'time']
		self.glue_sel_a = [DEFAULT_GLUE, DEFAULT_GLUE_CT]
		self.current_glue = DEFAULT_GLUE
		self.current_glue_ts = DEFAULT_GLUE_CT
		self.current_flow = DEFAULT_FLOW
		self.current_pressure = DEFAULT_PRESSURE
		
		self.glue_window = q_box(
							q_list, 
							t_list, 
							self, 
							'glue_sel_a', 
							exit_functions=['load_glue_sel']
							)
		
		self.glue_set_btn = QtGui.QPushButton('Set Glue')
		self.glue_set_btn.clicked.connect(self.set_glue)
		self.grid.addWidget(self.glue_set_btn, 9 + row_offset, 4)
		
		self.glue_label = QtGui.QLabel()
		self.glue_ts_label = QtGui.QLabel()
		self.grid.addWidget(self.glue_label, 9 + row_offset, 2)
		self.grid.addWidget(self.glue_ts_label, 9 + row_offset, 3)
		
		# Calibrate flow
		self.flow_cal_btn = QtGui.QPushButton('Calibrate')
		self.flow_window = fit_window(self)
		self.flow_cal_btn.clicked.connect(self.flow_cal)
		self.grid.addWidget(self.flow_cal_btn, 4 + row_offset, 4)
		self.position_cal_lb = QtGui.QLabel('Calibrate flow:')
		self.grid.addWidget(self.position_cal_lb, 4 + row_offset, 2)
		
		# Current flow and pressure labels
		self.current_pressure_lb = QtGui.QLabel()
		self.grid.addWidget(self.current_pressure_lb, 8 + row_offset, 2)
		self.current_flow_lb = QtGui.QLabel()
		self.grid.addWidget(self.current_flow_lb, 8 + row_offset, 3)
		self.load_last_glue()
		self.load_fandp_labels()
		
		# Init machine button
		self.machine_init_btn = QtGui.QPushButton('Init')
		self.machine_init_btn.clicked.connect(
			lambda: self.launch_worker(
				self.init_machine,
				starting_func = [self.load_machine]
				)
			)
		self.grid.addWidget(self.machine_init_btn, 10 + row_offset, 4)
		self.machine_init_lb = QtGui.QLabel('Init LitePlacer:')
		self.grid.addWidget(self.machine_init_lb, 10 + row_offset, 2)
		
		# park button
		self.machine_park_btn = QtGui.QPushButton('Park')
		self.machine_park_btn.clicked.connect(
			lambda: self.launch_worker(
				self.park,
				check_func = [
								self.init_warning,
							],
				)
			)
		self.grid.addWidget(self.machine_park_btn, 11 + row_offset, 4)
		self.machine_park_lb = QtGui.QLabel('Park LitePlacer:')
		self.grid.addWidget(self.machine_park_lb, 11 + row_offset, 2)
		
		# Draw button
		self.dry_run_speed_factor  = 1.
		self.dodraw_btn = QtGui.QPushButton('Draw')
		#self.dodraw_btn.clicked.connect(self.draw)
		self.dodraw_btn.clicked.connect(
			lambda: self.launch_worker(
				self.draw,
				check_func = [
					self.init_warning,
					self.coo_dict_warning,
					self.tilt_dict_warning,
					self.glue_type_warning,
					self.old_glue_warning,
					],
				)
			)
		self.grid.addWidget(self.dodraw_btn, 5 + row_offset, 4)
		
		# Dry run button
		self.dryrun_btn = QtGui.QPushButton('Dry Run')
		#self.dryrun_btn.clicked.connect(self.draw)
		self.dryrun_btn.clicked.connect(
			lambda: self.launch_worker(
				lambda: self.draw(dry_run=True),
				check_func = [
					self.init_warning,
					self.coo_dict_warning,
					self.tilt_dict_warning,
					#self.glue_type_warning,
					#self.old_glue_warning,
					self.ask_dry_run_speed,
					],
				)
			)
		self.grid.addWidget(self.dryrun_btn, 5 + row_offset, 3)
			
		# Draw label
		self.dodraw_lb = QtGui.QLabel('Draw configuration:')
		self.grid.addWidget(self.dodraw_lb, 5 + row_offset, 2)
		
		# Picture label
		self.takepic_lb = QtGui.QLabel('Take pictures:')
		self.grid.addWidget(self.takepic_lb, 6 + row_offset, 2)
		
		# Picture of glue button
		self.takepic_g_btn = QtGui.QPushButton('Glue')
		#self.dodraw_btn.clicked.connect(self.draw)
		self.takepic_g_btn.clicked.connect(
			lambda: self.launch_worker(
				self.take_glue_pictures,
				check_func = [
					self.init_warning,
					self.coo_dict_warning,
					self.tilt_dict_warning,
					],
				)
			)
		self.grid.addWidget(self.takepic_g_btn, 6 + row_offset, 4)
		
		# Loading at startup
		self.launch_worker(self.load_machine, toggle_func=self.toggle_move)
		#self.load_machine()
		self.launch_worker(self.load_scale, toggle_func=self.toggle_scale)
		
		self.show()
		print('Init took: '+str(time.time() - start_time )+' s')
		
	def choose_drawing(self, text):
		self.current_drawing = str(text)
		self.plot_ov()
		self.write_last_setup()
		
	def choose_jig(self, text):
		self.current_jig = str(text)
		self.plot_ov()
		self.load_pos_func_dict()
		self.load_dd_tilt_cal()
		self.load_tilt_dict()
		self.write_last_setup()
		
	def choose_grid(self, text):
		self.current_grid = str(text)
		self.plot_ov()
		self.load_dd_pos_cal()
		self.load_pos_func_dict()
		self.load_dd_tilt_cal()
		self.load_tilt_dict()
		self.write_last_setup()
		
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
		self.figure_ov_ax.clear()
		
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
			#total_offset_x += JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][0] 
			total_offset_x += JIG_CFG[self.current_jig]['probe']['p1'][0]
			total_offset_x += JIG_CFG[self.current_jig]['offsets']['drawing_position'][0]
			
			total_offset_y = GRID_CFG[self.current_grid][jig][1] 
			#total_offset_y += JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][1] 
			total_offset_y += JIG_CFG[self.current_jig]['probe']['p1'][1]
			total_offset_y += JIG_CFG[self.current_jig]['offsets']['drawing_position'][1]
			
			plt.text(
					total_offset_x, 
					total_offset_y -10, 
					str(jig), 
					ha='left',
					va='top',
					)
			
			for idx in range(len(x_l)):
				x_temp = [x + total_offset_x for x in x_l[idx]]
				y_temp = [y + total_offset_y for y in y_l[idx]]
				ax.plot(x_temp, y_temp, style)
				
		x_poffset = 0
		y_poffset = 50
		n_jig_x = max(int(self.current_grid.split('x')[0]), 4)
		n_jig_y = max(int(self.current_grid.split('x')[1]), 2)
		
		ax.set_xlim([x_poffset, x_poffset + 200*n_jig_x])
		ax.set_ylim([y_poffset, y_poffset + 200*n_jig_y])
		ax.set_aspect('equal', adjustable='box')
		self.canvas_ov.draw()
			
	def pos_cal(self):
		file_name = 'cache/CooFile_'+self.current_jig+'_'+self.current_grid+'.py'
		
		ret_code = make_jig_coord_grid_laser(
						self.machine, 
						self.laser_sensor,
						JIG_CFG[self.current_jig]['probe']['p1'],
						JIG_CFG[self.current_jig]['probe']['p2'],
						JIG_CFG[self.current_jig]['probe']['p3'],
						#JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][0], 
						#JIG_CFG[self.current_jig]['offsets']['coordinate_origin'][1], 
						up=JIG_CFG[self.current_jig]['offsets']['jig_hight'], 
						#up=5,
						#dx=JIG_CFG[self.current_jig]['probe']['dx'], 
						#dy=JIG_CFG[self.current_jig]['probe']['dy'], 
						dth=JIG_CFG[self.current_jig]['probe']['dth'], 
						probe_x=JIG_CFG[self.current_jig]['probe']['probe_x'], 
						probe_y=JIG_CFG[self.current_jig]['probe']['probe_y'], 
						cache_file=file_name,
						grid_dict=GRID_CFG[self.current_grid], 
						grid_idx=self.pos_cal_idx,
						#prb_h=1.5,
						)
		
		self.load_pos_func_dict()
	
	def laser_cal(self):
		file_name = 'cache/CooFile_'+self.current_jig+'_'+self.current_grid+'.py'
		cal_pos_x = [LASER_CAL_POSITION_X[0]-self.laser_sensor.get_dx0(), LASER_CAL_POSITION_X[1]-self.laser_sensor.get_dy0()]
		cal_pos_y = [LASER_CAL_POSITION_Y[0]-self.laser_sensor.get_dx0(), LASER_CAL_POSITION_Y[1]-self.laser_sensor.get_dy0()]
		
		# 25/10/2021 home to reset accuracy (motor turn off)
		self.machine.home()
		
		lx = self.laser_sensor.EdgeDetection(self.machine, cal_pos_x, 10, 'x', 'Laser', 3, ToolsWidth=0.890) #height jig 15+0.5
		ly = self.laser_sensor.EdgeDetection(self.machine, cal_pos_y, 10, 'y', 'Laser', 3, ToolsWidth=0.890)
		nx = self.laser_sensor.EdgeDetection(self.machine, LASER_CAL_POSITION_X, 10, 'x', 'Needle', 3, ToolsWidth=0.890)
		ny = self.laser_sensor.EdgeDetection(self.machine, LASER_CAL_POSITION_Y, 10, 'y', 'Needle', 3, ToolsWidth=0.890)

		laserxy = [lx,ly]
		needlexy = [nx,ny]
		##laserxy =[-37.728,8.727]
		##needlexy = [1.345,72.025]
		self.laser_sensor.SetXYOffset(laserxy,needlexy)
    
  
		#LaserSensor.set_dxy0(39.647,64.452)
		self.laser_sensor.ZCalibration(self.machine,LASER_CAL_POSITION_Y[0],LASER_CAL_POSITION_Y[1],aprxHightOfObject=3)
		#pass
		
		self.write_last_laser_cal()
	
	def tilt_cal(self):
		file_name = 'cache/CooFile_'+self.current_jig+'_'+self.current_grid+'.py'
		max_hight = TABLE_HIGHT - JIG_CFG[self.current_jig]['offsets']['jig_hight'] - JIG_CFG[self.current_jig]['tilt']['max_height']
		
		if 'all' in self.tilt_cal_idx:
			to_do = []
			for jig in GRID_CFG[self.current_grid]:
			    if isinstance(jig, int): to_do.append(jig)
			to_do.sort()	
		else:
			to_do = [self.tilt_cal_idx]
		
		for jig in to_do:
			if self.pos_func_dict[jig] is None: continue
			
			# 25/10/2021 home to reset accuracy (motor turn off)
			self.machine.home()
			
			ret_code = make_jig_tilt_grid_laser(
						self.machine, 
						self.laser_sensor,
						JIG_CFG[self.current_jig]['tilt']['p1'], 
						JIG_CFG[self.current_jig]['tilt']['p2'],  
						JIG_CFG[self.current_jig]['tilt']['p3'],  
						coord_func_dict=self.pos_func_dict, 
						cache_file=file_name, 
						grid_dict=GRID_CFG[self.current_grid], 
						grid_idx=jig
						)
		
		self.load_tilt_dict()

	def load_dd_draw(self):
		self.draw_dd.clear()
		for drawing in DRAWING_CFG:
			self.draw_dd.addItem(drawing)
		self.draw_dd.setCurrentIndex(DRAWING_CFG.keys().index(self.current_drawing))
		
	def load_dd_jig(self):
		self.jig_dd.clear()
		for jig in JIG_CFG:
			self.jig_dd.addItem(jig)
		self.jig_dd.setCurrentIndex(JIG_CFG.keys().index(self.current_jig))
		
	def load_dd_grid(self):
		self.grid_dd.clear()
		for grid in GRID_CFG:
			self.grid_dd.addItem(grid)
		self.grid_dd.setCurrentIndex(GRID_CFG.keys().index(self.current_grid))
		
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
		
	def load_tilt_dict(self):
		file_name = 'cache/CooFile_'+self.current_jig+'_'+self.current_grid+'.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
		except:
			read_data = {}
		
		tilt_dict = {}
		for jig in GRID_CFG[self.current_grid]:
			if not isinstance(jig, int): continue
			#if unicode(jig) in read_data and not read_data[unicode(jig)]['tilt_map'] is None:
			if unicode(jig) in read_data and 'tilt_map' in read_data[unicode(jig)]:
				tilt_dict[jig] = {}
				tilt_dict[jig]['tilt_map'] = read_data[unicode(jig)]['tilt_map']
				tilt_dict[jig]['tilt_map_og'] = read_data[unicode(jig)]['tilt_map_og']
			else: tilt_dict[jig] = None
		
		self.tilt_dict = tilt_dict
		print(self.tilt_dict)
		
	def load_fandp_labels(self):
		try:
			self.current_flow_lb.setText('Flow: {:5.2f} mg/s'.format(self.current_flow))
		except:
			self.current_flow_lb.setText('Flow: {:5.2f} mg/s'.format(self.current_flow))
			self.current_flow_lb.setText('Flow:  none mg/s')
		
		try:
			self.current_pressure_lb.setText('Pressure: {:4.0f} mbar'.format(self.current_pressure))
		except:
			self.current_pressure_lb.setText('Pressure: {:4.0f} mbar'.format(self.current_pressure))
			self.current_pressure_lb.setText('Pressure: none mbar')
			
		try:
			self.glue_label.setText('Glue: '+ self.current_glue)
		except:
			self.glue_label.setText('Glue: '+ self.current_glue)
		
		try:
			self.glue_ts_label.setText('From: ' + ts_to_timestr(self.current_glue_ts, option='%d %b %H:%M'))
		except:
			self.glue_ts_label.setText('From: ' + ts_to_timestr(self.current_glue_ts, option='%b %d %H:%M'))
			self.glue_ts_label.setText('From:       none' )
						
	def init_machine(self):
		self.machine.init_code()
	
	def load_machine(self):
		#self.machine = gcode_handler()
		#self.machine = None
		self.reload_cfg()
		try:
			self.machine = gcode_handler()
		except:
			print('Machine not made')
			#self.machine = None
			pass
		#print('current sel.machine: ', self.machine)
			
	def load_scale(self):
		# print('Loading scale')
		# self.scale = scale_handler(False)
		# self.new_glue_to_log()
		# print('scale loaded')
		try:
			self.scale = scale_handler(False)
			self.new_glue_to_log()
		except:
			print('Scale not made')
			self.scale = None
			pass
			
	def load_laser_sensor(self):
		print('Loading laser sensor')
		# self.scale = scale_handler(False)
		# self.new_glue_to_log()
		# print('scale loaded')
		try:
			self.laser_sensor = LaserSensor('COM8')
		except:
			print('LaserSensor not made')
			self.laser_sensor = None
			pass
	
	def set_glue(self):
		self.disable_all()
		self.glue_window.show()
		
	def load_glue_sel(self):
		self.current_glue = self.glue_sel_a[0]
		print(self.glue_sel_a)
		if isinstance(self.glue_sel_a[1], str):
			self.current_glue_ts = timestr_to_ts(self.glue_sel_a[1])
		else: self.current_glue_ts = None
		if self.current_glue == 'None':
			self.current_pressure = 0
			self.current_flow = float(DRAWING_CFG[self.current_drawing]['desired_flow'])
		self.new_glue_to_log()
		self.load_fandp_labels()
		print(self.glue_sel_a)
		print(self.current_glue, self.current_glue_ts)
		self.write_last_glue()
		
	def load_last_glue(self):
		file_name = 'cache/FlowFile.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
		except:
			read_data = {}
		
		self.current_flow     = DEFAULT_FLOW
		self.current_pressure = DEFAULT_PRESSURE
		self.current_glue     = DEFAULT_GLUE
		self.current_glue_ts  = DEFAULT_GLUE_CT
		for key in read_data:
			if 'last_glue' in key: 
				
				self.current_flow     = read_data[key]['flow']
				self.current_pressure = read_data[key]['pressure']
				self.current_glue     = read_data[key]['type']
				self.current_glue_ts  = read_data[key]['ts']
		
		self.load_fandp_labels()
		
	def load_last_laser_cal(self):
		file_name = 'cache/LaserSensor_calibration.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
			self.laser_sensor.set_dxy0(read_data['dx0'], read_data['dy0'])
			self.laser_sensor.CalibrationCoefficient = read_data['z_cal']
		except:
			read_data = {}
	
	def write_last_glue(self):
		file_name = 'cache/FlowFile.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
		except:
			read_data = {}
		
		new_data = copy.deepcopy(read_data)
		new_data['last_glue'] = {}
		new_data['last_glue']['flow']     = self.current_flow
		new_data['last_glue']['pressure'] = self.current_pressure
		new_data['last_glue']['type']     = self.current_glue
		new_data['last_glue']['ts']       = self.current_glue_ts
		
		ff_file = open(file_name, 'w')
		ff_file.write(json.dumps(new_data, indent=2))
		ff_file.close()
		
	def write_last_laser_cal(self):
		file_name = 'cache/LaserSensor_calibration.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
			
		except:
			read_data = {}
		
		new_data = copy.deepcopy(read_data)
		new_data['dx0'] = self.laser_sensor.get_dx0()
		new_data['dy0'] = self.laser_sensor.get_dy0()
		new_data['z_cal'] = self.laser_sensor.CalibrationCoefficient
		
		if not read_data == {}:
			print('Laser calibration changes:')
			print('-- new dx0: '+str(new_data['dx0']))
			print('-- old dx0: '+str(read_data['dx0']))
			print('-- new dy0: '+str(new_data['dy0']))
			print('-- old dy0: '+str(read_data['dy0']))
			print('-- new z_cal: '+str(new_data['z_cal']))
			print('-- old z_cal: '+str(read_data['z_cal']))
		
		ff_file = open(file_name, 'w')
		ff_file.write(json.dumps(new_data, indent=2))
		ff_file.close()
			
	def new_glue_to_log(self):
		self.scale.flow_log_new_glue(self.current_glue, self.current_glue_ts)
	
	def load_flow_and_pres(self):
		file_name = 'cache/FlowFile.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
		except:
			read_data = {}
		
		#self.current_flow = None
		#self.current_pressure = None
		for key in read_data:
			if self.current_glue in key: 
				self.current_flow = read_data[key]['flow']
				self.current_pressure = read_data[key]['pressure']
		
		self.load_fandp_labels()
			
	def write_flow_and_pres(self):
		file_name = 'cache/FlowFile.py'
		
		try:
			ff_file = open(file_name, 'r')
			read_data = json.load(ff_file)
			ff_file.close()
		except:
			read_data = {}
			
		new_data = copy.deepcopy(read_data)
		new_data[self.current_glue] = {'flow': self.current_flow, 'pressure': self.current_pressure}
		
		ff_file = open(file_name, 'w')
		ff_file.write(json.dumps(new_data, indent=2))
		ff_file.close()
	
	def flow_cal(self):
		self.disable_all()
		
		if self.machine is None:
			self.init_warning()
			self.enable_all()
			return
		
		if not self.old_glue_warning(): 
			self.enable_all()
			return
			
		if not self.none_glue_warning():
			self.enable_all()
			return
		
		if not self.glue_type_warning():
			self.enable_all()
			return
		
		#self.flow_window = fit_window(self)
		# print('fit w made')
		# if self.scale is None:
			# self.scale = scale_handler(False)
			# self.new_glue_to_log()
		# print('scale connected')
		self.flow_window.clear_window()
		self.flow_window.show()

	def park(self):
		self.machine.up()
		self.machine.gotoxy(PARK_POSITION[0], PARK_POSITION[1])
		
	def ask_dry_run_speed(self):
		dry_run_factor = 5.
		choise = QtGui.QMessageBox.question(
						self, 
						'Dry Run speed', 
						'Would you like to draw the dry run '+str(dry_run_factor)+' times faster?',
						QtGui.QMessageBox.No | QtGui.QMessageBox.Yes 
						)
		if choise == QtGui.QMessageBox.Yes:
			self.dry_run_speed_factor = dry_run_factor
		else: self.dry_run_speed_factor  = 1.
		return True
		
		
	def draw(self, dry_run=False, speed_factor=1.):
		
		speed_factor = 1.
		if dry_run:
			speed_factor = self.dry_run_speed_factor	
		
		self.machine.home()
		for jig in GRID_CFG[self.current_grid]:
			if not isinstance(jig, int): continue
			if self.pos_func_dict[jig] is None: continue
			if self.tilt_dict[jig]['tilt_map'] is None: continue
			
			self.machine.tilt_map = self.tilt_dict[jig]['tilt_map']
			self.machine.tilt_map_og = self.tilt_dict[jig]['tilt_map_og']
			
			needle_bend = calc_bend(self.tilt_speed, 'cache/'+self.current_bend_file)
			object_h = self.machine.tilt_map_og[2] - JIG_CFG[self.current_jig]['drawing']['hight'] - needle_bend
			image_h = object_h - DRAWING_CFG[self.current_drawing]['above']
			imoge_o = sum_offsets(GRID_CFG[self.current_grid][jig], JIG_CFG[self.current_jig]['offsets']['drawing_position'])
			print('image_offset: '+str(GRID_CFG[self.current_grid][jig])+' + '+str(JIG_CFG[self.current_jig]['offsets']['drawing_position']) + ' = '+str(imoge_o))
			
			image = drawing2(
						DRAWING_CFG[self.current_drawing]['file'], 
						offset=imoge_o, 
						hight=image_h, 
						coord_func=self.pos_func_dict[jig], 
						clean_point=[0, 0, TABLE_HIGHT-1]
						)
			
			image_l = image.layer_line_length(DRAWING_CFG[self.current_drawing]['layer'])
			image_m = DRAWING_CFG[self.current_drawing]['mass']
			draw_speed = speed_factor*(image_l+0.)/(((image_m+0.)/(self.current_flow+0))/60.) # in mm/min
			
			delay = 0.01
			if 'SY186' in self.current_glue or DRAWING_CFG[self.current_drawing]['is_encap']: delay = 1
			if 'PT601' in self.current_glue and self.current_pressure < 200: delay = 0.5
			ask_r = False
			up_f = True
			
			draw_pressure = self.current_pressure
			if dry_run: draw_pressure = 0
			
			image.draw_robust(
				self.machine,
				draw_pressure,
				draw_speed, 
				layer=DRAWING_CFG[self.current_drawing]['layer'], 
				delay=delay, 
				up_first=up_f, 
				ask_redo=ask_r,
				)
		self.machine.up()
		self.machine.gotoxy(SCALE_POSITION[0], SCALE_POSITION[1])
		
	def take_glue_pictures(self):
		
		#self.machine.home()
		for jig in GRID_CFG[self.current_grid]:
			if not isinstance(jig, int): continue
			if self.pos_func_dict[jig] is None: continue
			if self.tilt_dict[jig]['tilt_map'] is None: continue
			
			self.machine.tilt_map = self.tilt_dict[jig]['tilt_map']
			self.machine.tilt_map_og = self.tilt_dict[jig]['tilt_map_og']
			
			needle_bend = calc_bend(self.tilt_speed, 'cache/'+self.current_bend_file)
			print('Compensation for needle bend: '+str(needle_bend))
			object_h = self.machine.tilt_map_og[2] - JIG_CFG[self.current_jig]['drawing']['hight'] - needle_bend
			image_h = object_h - DRAWING_CFG[self.current_drawing]['above']
			imoge_o = sum_offsets(GRID_CFG[self.current_grid][jig], JIG_CFG[self.current_jig]['offsets']['drawing_position'])
			#print('image_offset: '+str(GRID_CFG[self.current_grid][jig])+' + '+str(JIG_CFG[self.current_jig]['offsets']['drawing_position']) + ' = '+str(imoge_o))
			
			image = drawing2(
						DRAWING_CFG[self.current_drawing]['file'], 
						offset=imoge_o, 
						hight=image_h, 
						coord_func=self.pos_func_dict[jig], 
						clean_point=[0, 0, TABLE_HIGHT-1]
						)
			
			layer = DRAWING_CFG[self.current_drawing]['picture_layer']
			
			locations = image.get_picture_locations(
				layer
				)
				
			for idx,loc in enumerate(locations):
				# Move to location
				self.machine.move_camera_xy(loc[0], loc[1])
				
				time.sleep(0.2)
				# Take picture
				image = self.take_picture()
			
				# Process image
				time_stamp = datetime.datetime.now().strftime("%H_%M_%S")
				name = '_'.join([ 'time', time_stamp, 'GluePicture', str(self.current_drawing), 'jig', str(jig), 'picture', str(idx)])
				name += '.png'
				path = self.get_picture_path()
				self.save_picture(name, image, path)
				
			
		self.machine.up()
		self.machine.gotoxy(SCALE_POSITION[0], SCALE_POSITION[1])
	
	def toggle_all(self, bool):
		self.jig_dd.setEnabled(bool)
		self.grid_dd.setEnabled(bool)
		self.draw_dd.setEnabled(bool)
		self.cfg_btn.setEnabled(bool)
		
		self.laser_cal_btn.setEnabled(bool)
		
		self.pos_cal_idx_dd.setEnabled(bool)
		self.position_cal_btn.setEnabled(bool)
		
		self.tilt_cal_idx_dd.setEnabled(bool)
		self.tilt_cal_btn.setEnabled(bool)
		
		self.flow_cal_btn.setEnabled(bool)
		self.dodraw_btn.setEnabled(bool)
		self.dryrun_btn.setEnabled(bool)
		self.takepic_g_btn.setEnabled(bool)
		
		self.glue_set_btn.setEnabled(bool)
		self.machine_park_btn.setEnabled(bool)
		self.machine_init_btn.setEnabled(bool)
		self.update()
		
	def toggle_move(self, bool):
		
		self.laser_cal_btn.setEnabled(bool)
		
		self.position_cal_btn.setEnabled(bool)
		
		self.tilt_cal_btn.setEnabled(bool)
		
		#self.flow_cal_btn.setEnabled(bool)
		self.dodraw_btn.setEnabled(bool)
		self.dryrun_btn.setEnabled(bool)
		self.takepic_g_btn.setEnabled(bool)
		
		self.machine_park_btn.setEnabled(bool)
		self.machine_init_btn.setEnabled(bool)
		self.update()
		
	def toggle_scale(self, bool):
		
		self.flow_cal_btn.setEnabled(bool)
		self.update()
	
	def enable_all(self):
		self.toggle_all(True)
		
	def disable_all(self):
		self.toggle_all(False)

	def update(self):
		self.repaint()
		self.app.processEvents()
		
	def reload_cfg(self):
		print('Reloading config')
		global DRAWING_CFG
		global JIG_CFG
		global GRID_CFG
		
		reload(glueing_cfg)
		from glueing_cfg import DRAWING_CFG, JIG_CFG, GRID_CFG
		time.sleep(0.5)
		
	def load_last_setup(self):
		file_name = 'cache/LastSetupFile.py'
		
		try:
			func_file = open(file_name, 'r')
			read_data = json.load(func_file)
			func_file.close()
		except:
			read_data = None
		
		self.current_grid    = DEFAULT_GRID
		self.current_jig     = DEFAULT_JIG
		self.current_drawing = DEFAULT_DRAWING
		if not read_data is None:
			self.current_grid    = read_data['grid']
			self.current_jig     = read_data['jig']
			self.current_drawing = read_data['drawing']
		
		self.load_dd_grid()
		self.load_dd_jig()
		self.load_dd_draw()
		
	def write_last_setup(self):
		file_name = 'cache/LastSetupFile.py'
			
		new_data = {}
		new_data['grid']    = self.current_grid
		new_data['jig']     = self.current_jig 
		new_data['drawing'] = self.current_drawing 
		
		ff_file = open(file_name, 'w')
		ff_file.write(json.dumps(new_data, indent=2))
		ff_file.close()

	def init_warning(self):
		if self.machine is None:
			QtGui.QMessageBox.information(
						self, 
						'LitePlacer not found', 
						'Initiate the LitePlacer before you can do this operation.',
						QtGui.QMessageBox.Ok
						)
			return False
		else: return True
		
	def coo_dict_warning(self):
		missing_jig = []
		present_jig = []
		for jig in self.pos_func_dict:
			if self.pos_func_dict[jig] is None:
				missing_jig.append(str(jig))
			else: present_jig.append(str(jig))
		
		if len(missing_jig) == len(self.pos_func_dict):
			QtGui.QMessageBox.information(
					self, 
					'Position not found', 
					'Missing position calibration of all jigs\n Operation canceled.',
					QtGui.QMessageBox.Ok
					)
			return False
		elif len(missing_jig) > 0:
			missing_str = ', '.join(missing_jig)
			present_str = ', '.join(present_jig)
			QtGui.QMessageBox.information(
					self, 
					'Position not found', 
					'Missing position calibration of jig\'s ['+missing_str+']\n Jig\'s ['+missing_str+ '] will be skipped.\n Proceeding with jig\'s ['+present_str+'].',
					QtGui.QMessageBox.Ok
					)
			return True
		else: return True
	
	def tilt_dict_warning(self):
		missing_jig = []
		present_jig = []
		for jig in self.pos_func_dict:
			if self.tilt_dict[jig] is None:
				missing_jig.append(str(jig))
			else: present_jig.append(str(jig))
		
		if len(missing_jig) == len(self.pos_func_dict):
			QtGui.QMessageBox.information(
					self, 
					'Tilt not found', 
					'Missing tilt calibration of all jigs\n Operation canceled.',
					QtGui.QMessageBox.Ok
					)
			return False
		elif len(missing_jig) > 0:
			missing_str = ', '.join(missing_jig)
			present_str = ', '.join(present_jig)
			QtGui.QMessageBox.information(
					self, 
					'Tilt not found', 
					'Missing tilt calibration of jig\'s ['+missing_str+']\n Jig\'s ['+missing_str+ '] will be skipped.\n Proceeding with jig\'s ['+present_str+'].',
					QtGui.QMessageBox.Ok
					)
			return True
		else: return True
		
	def old_glue_warning(self):
		if self.current_glue == 'None': return True
		if self.current_glue == 'WATER': return True
		old = 4*60*60
		if not time.time() - self.current_glue_ts > old: return True
		else:
			#parent = QtGui.QMainWindow()
			choise = QtGui.QMessageBox.information(
							self, 
							'Old glue detected', 
							'Time stamp for this glue is older then '+str(old/60)+' min.',
							QtGui.QMessageBox.Abort | QtGui.QMessageBox.Ignore 
							)
			if choise == QtGui.QMessageBox.Ignore:
				return True
			else:
				return False
	
	def none_glue_warning(self):
		if self.current_glue == 'None':
			#parent = QtGui.QMainWindow()
			choise = QtGui.QMessageBox.information(
							self, 
							'Glue type "None" detected', 
							'Unexpected operation for glue type "None"',
							QtGui.QMessageBox.Abort | QtGui.QMessageBox.Ignore 
							)
			if choise == QtGui.QMessageBox.Ignore:
				return True
			else:
				return False
		else: return True
	
	#DRAWING_CFG
	def glue_type_warning(self):
		if self.current_glue == 'None': return True
		if not DRAWING_CFG[self.current_drawing]['expected_glue'] == self.current_glue:
			#parent = QtGui.QMainWindow()
			choise = QtGui.QMessageBox.information(
							self, 
							'Glue type mismatch detected', 
							'Current glue type is "'+self.current_glue+'", while "'+DRAWING_CFG[self.current_drawing]['expected_glue']+'" was expected',
							QtGui.QMessageBox.Abort | QtGui.QMessageBox.Ignore 
							)
			if choise == QtGui.QMessageBox.Ignore:
				return True
			else:
				return False
		else: return True

	def launch_worker(self, function, check_func=[], starting_func=[], closing_func=[], toggle_func=None):
		if toggle_func is None:
			enable_func = self.toggle_all
		else:
			enable_func = toggle_func
		
		enable_func(False)
		
		run = True
		for func in check_func:
			check = func()
			if not check: 
				run = False
				break
		
		if run: 
			for func in starting_func:
				func()
				
			worker = Worker(function)
			worker.signals.finished.connect(lambda: self.worker_finished(closing_func, enable_func))
			worker.signals.error.connect(self.worker_error)
			self.thread_pool.start(worker)
			return
		else:
			enable_func(True)
		
	def worker_finished(self, func_list, enable_func):
		enable_func(True)
		for func in func_list:
			func()
	
	def worker_error(self, type_str, message):
		QtGui.QMessageBox.warning(
						self, 
						'Error: '+type_str, 
						message,
						QtGui.QMessageBox.Ok
						)
		

	def load_menu(self):
		# Bend menu
		bend_menu = self.menu_bar.addMenu('Bend')
		bend_sel = bend_menu.addMenu("Set needle bend file")
		action_group = QtGui.QActionGroup(self, exclusive=True)
		for file in os.listdir('cache/'):
			if 'NeedleBend' in file:
				action = QtGui.QAction(file, bend_sel, checkable=True)
				if file == self.current_bend_file: action.setChecked(True)
				action.triggered.connect(lambda checked, var=file: self.set_bend_file(var))
				men_a = action_group.addAction(action)
				bend_sel.addAction(men_a)
				
		# Test menu
		test_menu = self.menu_bar.addMenu('Test/Measure')
		for idx,test in enumerate(TEST_LIST):
			print(type(test))
			action = QtGui.QAction(test.__name__, test_menu)
			#test_obj = test(self)
			action.triggered.connect(lambda var=idx: self.select_test(var))
			test_menu.addAction(action)
			#print(test.__name__)
			
		# Inspect menu
		insp_menu = self.menu_bar.addMenu('Inspect')
		action = QtGui.QAction('Open window', insp_menu)
		action.triggered.connect(self.open_inspect_window)
		insp_menu.addAction(action)
		
		# Scale menu
		scale_menu = self.menu_bar.addMenu('Scale')
		action = QtGui.QAction('Open window', scale_menu)
		action.triggered.connect(self.open_scale_window)
		scale_menu.addAction(action)
		
		
	# Camera stuff
	def take_picture(self):
		# Take picture to flush buffer
		success_tmp, image_tmp = self.webcam.read()
		#print('Taking pic')
		attempt = 0
		success = False
		while not success and attempt < 10:
			success, image = self.webcam.read()
			if not success: time.sleep(0.5)
			attempt += 1
		image_r = cv2.rotate(image, cv2.ROTATE_180)
		#image.rotate(180)
		return image_r
		
	def save_picture(self, name, image, path):
		cv2.imwrite(path+name, image)
		
	def get_picture_path(self):
		path = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue-no-timeout\\images\\webcam\\'
		path += datetime.datetime.now().strftime("%Y_%b_%d") + '\\'
		
		# Make day folder if not there yet
		if not os.path.isdir(path): os.mkdir(path)
		return path
		
	
	def set_bend_file(self, file):
		self.current_bend_file = file
		
	def select_test(self, test_idx):
		#print(type(test))
		test_obj = TEST_LIST[test_idx](self.test_window, self)
		self.test_window.set_test(test_obj)
		self.test_window.show()
		
	def open_inspect_window(self):
		self.insp_window.start_stream()
		self.insp_window.load_current_position
		self.insp_window.show()
		
	def open_scale_window(self):
		self.scale_window.start_stream()
		self.scale_window.show()

		
class q_box(QtGui.QWidget):

	def __init__(self, q_list, t_list, main_window, attr_name, exit_functions=[], pix_w=500, pix_h=200, parent=None):
		print('init q_box')
		super(q_box, self).__init__(parent)
		self.setGeometry(50, 50, pix_w, pix_h)
		self.setWindowTitle("GLUI: info")
		self.setWindowIcon(QtGui.QIcon('images/GLUI_logo.png'))
		self.setPalette(PALETTE)
		
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
		self.main_window.load_flow_and_pres()
		self.main_window.enable_all()
		self.close()
	
	def closeEvent(self, event):
		self.main_window.enable_all()
		event.accept()

		
class fit_window(QtGui.QWidget):

	def __init__(self, main_window, guess_pressure=False, pix_w=700, pix_h=500, parent=None):
		print('fit window')
		super(fit_window, self).__init__(parent)
		self.setWindowTitle("GLUI: flow calibration")
		self.setWindowIcon(QtGui.QIcon('images/GLUI_logo.png'))
		self.setPalette(PALETTE)
		
		self.setGeometry(50, 50, pix_w, pix_h)
		self.main_window = main_window
		self.desired_flow = DRAWING_CFG[main_window.current_drawing]['desired_flow']
		self.flow_precision = DRAWING_CFG[main_window.current_drawing]['flow_precision']
		if guess_pressure and not main_window.current_pressure is None:
			self.set_pressure = main_window.current_pressure
			self.guess_pressure(main_window.current_flow)
		else:
			self.set_pressure = DRAWING_CFG[main_window.current_drawing]['init_pressure']
		self.measured_flow = 0.
		self.max_factor = 1.5
		self.needle_clear = False
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		self.thread_pool = QtCore.QThreadPool()
		
		# Fit plot
		self.figure, self.figure_ax = plt.subplots() 
		#self.figure_ov = plt.figure(figsize=(10,5))
		self.canvas = Canvas(self.figure)
		self.grid.addWidget(self.canvas, 0, 0, 1, 3)
		#self.canvas.draw()
		
		# Progress and eta
		self.progress_bar = QtGui.QProgressBar()
		self.progress_bar.setAlignment(QtCore.Qt.AlignRight)
		self.grid.addWidget(self.progress_bar, 2, 1, 1, 2)
		self.eta_lb = QtGui.QLabel('ETA:  none s')
		self.grid.addWidget(self.eta_lb, 2, 0)
		
		# Info labels
		self.pressure_lb = QtGui.QLabel()
		self.grid.addWidget(self.pressure_lb, 1, 0)
		
		self.flow_lb = QtGui.QLabel()
		self.grid.addWidget(self.flow_lb, 1, 1)
		
		self.desired_flow_lb = QtGui.QLabel()
		self.grid.addWidget(self.desired_flow_lb, 1, 2)
		self.update_labels()
		
		
		# Start button 
		self.start_btn = QtGui.QPushButton('Start')
		self.start_btn.clicked.connect(self.start)
		self.start_btn.setEnabled(True)
		self.grid.addWidget(self.start_btn, 3, 0)
		
		# Good fit/ Bad fit buttons
		self.good_btn = QtGui.QPushButton('Good')
		self.good_btn.clicked.connect(self.good)
		self.good_btn.setEnabled(False)
		self.grid.addWidget(self.good_btn, 3, 1)
		self.bad_btn = QtGui.QPushButton('Bad')
		self.bad_btn.clicked.connect(self.bad)
		self.bad_btn.setEnabled(False)
		self.grid.addWidget(self.bad_btn, 3, 2)
	
	def calibrate_scale(self):
		self.main_window.scale.zero()
		#self.main_window.scale.send_command('C')
		self.main_window.scale.calibrate()
		#time.sleep(20)
		# QtGui.QMessageBox.information(
						# self, 
						# 'Calibration mass', 
						# 'Put 1 g calibration mass on the scale.',
						# QtGui.QMessageBox.Ok
						# )
		# self.main_window.scale.cal_noq('g')
		# QtGui.QMessageBox.information(
						# self, 
						# 'Calibration mass', 
						# 'Remove calibration mass from the scale.',
						# QtGui.QMessageBox.Ok
						# )
				
	def update_labels(self):
		self.pressure_lb.setText('Set pressure: {:4.0f} mbar'.format(self.set_pressure))
		self.flow_lb.setText('Measured flow: {:5.2f} mg/s'.format(self.measured_flow))
		self.desired_flow_lb.setText('Desired flow: {:5.2f} mg/s'.format(self.desired_flow))
	
	def move_to_scale(self):
		self.main_window.machine.gotoxy(position=SCALE_POSITION)
		self.main_window.machine.down(7)
		scale_height = self.main_window.machine.probe_z(speed=50)[2]
		needle_height = scale_height - 2
		#needle_height = scale_height - 1
		if not self.needle_clear: self.clear_needle()
		self.main_window.machine.down(needle_height)
		# pass
		
	def clear_needle(self, duration=1):
		self.main_window.machine.set_pressure(self.set_pressure*2, no_flush=False)
		time.sleep(duration)
		self.main_window.machine.stop_pressure()
		self.needle_clear = True
			
	def start(self):
		self.start_btn.setEnabled(False)
		self.update()
		self.calibrate_scale()
		self.move_to_scale()
		self.flow_iteration()	

	#def clear_needle(self):
	#	self.main_window.scale.zero()
		
	def flow_iteration(self):
		time.sleep(1)
		self.main_window.scale.zero()
		time.sleep(1)
		mass_lim = 150
		#mass_lim = 300
		if self.main_window.current_glue == 'SY186': mass_lim = 500
		if self.main_window.current_glue == 'WATER': mass_lim = 500
		time_out = max((mass_lim + 50 + 0.)/((self.desired_flow + 0.)/2.), 100)
		
		#plt.cla()
		#self.figure_ax.clear()
		
		self.scale_data = []
		worker_func = lambda signal: self.main_window.scale.read_out_flow_GUI2(
			self.main_window.machine, 
			#check rest
			self.set_pressure, 
			3, # second to wait before and after
			mass_lim, 
			signal, 
			#n_data=9000,
			#n_data=1000,
			n_data=2500,
			display=True, 
			dt_print=0.5, 
			time_out=time_out
			)
		self.launch_worker(
			worker_func, 
			toggle_func = self.toggle_good_bad,
			closing_func = [self.fit_flow]
			)
		# flow = measure_flow_GUI(
				# self.main_window.machine, 
				# self.main_window.scale, 
				# self.set_pressure, 
				# 3, # second to wait before and after
				# mass_lim, 
				# 20, 
				# self.figure_ax, 
				# self.progress_bar, 
				# self.eta_lb,
				# time_out=time_out
				# )
		# self.measured_flow = flow
		# self.update_labels()
		
		# self.canvas.draw()
		# self.good_btn.setEnabled(True)
		# self.bad_btn.setEnabled(True)
		# self.update()

	def plot_data(self, extra_plots=None, text=None):
		self.figure_ax.clear()
		self.main_window.scale.load_data_to_axis(
			self.scale_data, 
			self.figure_ax, 
			extra_plots=extra_plots, 
			text=text
			)
		self.canvas.draw()
		
	def fit_flow(self):
		#ret_dict = calc_delay_and_flow(
		#			self.scale_data, 
		#			0./1000., 	# mass threshold
		#			self.main_window.scale, 
		#			3, 			# second to wait before and after
		#			False
		#			)
		#			#False		# low flow 
		ret_dict = calc_flow(self.scale_data)
		#delay = ret_dict['delay']
		flow = ret_dict['flow']
		#flow_int = ret_dict['flow_int']
		x_sim = ret_dict['x_sim']
		y_sim = ret_dict['y_sim']
		#y_sim_up = ret_dict['y_sim_up']
		#y_sim_dn = ret_dict['y_sim_dn']
		redo = ret_dict['redo']
		x_st = ret_dict['x_st']
		x_fi = ret_dict['x_fi']
		y_st = ret_dict['y_st']
		if not redo:
			lin_fit = {}
			lin_fit['Fit_x'] = x_sim
			lin_fit['Fit_y'] = y_sim
			lin_fit['Fit_style'] = 'r'
			#lin_fit['Fit Up_x'] = x_sim
			#lin_fit['Fit Up_y'] = y_sim_up
			#lin_fit['Fit Up_style'] = 'y--'
			#lin_fit['Fit Down_x'] = x_sim
			#lin_fit['Fit Down_y'] = y_sim_dn
			#lin_fit['Fit Down_style'] = 'y--'
			if not x_st[0] is None:
				lin_fit['Pressure ON_x'] = x_st
				lin_fit['Pressure ON_y'] = y_st
				lin_fit['Pressure ON_style'] = 'c--'
				lin_fit['Pressure OFF_x'] = x_fi
				lin_fit['Pressure OFF_y'] = y_st
				lin_fit['Pressure OFF_style'] = 'c--'
			
			fit_text = '{:.1f} mg/s \n{:.1f} mbar'.format(flow, self.set_pressure)

			self.plot_data(extra_plots=lin_fit, text=fit_text)
			#scale.write_flow_log(pressure, flow, delay)
			self.measured_flow = flow
		else:
			self.plot_data()
			#scale.load_data_to_axis(data, axis)
			self.measured_flow = 0.
					
	def good(self):
		self.good_btn.setEnabled(False)
		self.bad_btn.setEnabled(False)
		self.update()
		self.main_window.scale.write_flow_log(self.set_pressure, self.measured_flow, 9999.)
		
		if abs(self.measured_flow - self.desired_flow) < self.flow_precision:
			self.accept_flow()
		else:
			parent = QtGui.QMainWindow()
			choise = QtGui.QMessageBox.question(
							self, 
							'Proceed to next iteration?', 
							'Do you want to take this flow, or do you want to proceed with the next iteration to the desired flow?',
							QtGui.QMessageBox.Apply | QtGui.QMessageBox.Retry
							)
			if choise == QtGui.QMessageBox.Apply:
				self.accept_flow()
			else:
				self.guess_pressure(self.measured_flow)
				self.flow_iteration()

	def accept_flow(self):
		self.main_window.current_flow = self.measured_flow
		self.main_window.current_pressure = self.set_pressure
		self.main_window.load_fandp_labels()
		self.main_window.write_last_glue()
		self.main_window.write_flow_and_pres()
		self.close_window()
			
	def bad(self):
		self.good_btn.setEnabled(False)
		self.bad_btn.setEnabled(False)
		self.update()
		
		parent = QtGui.QMainWindow()
		choise = QtGui.QMessageBox.question(
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
		self.update_labels()
	
	def close_window(self):
		self.main_window.machine.up()
		self.main_window.enable_all()
		self.start_btn.setEnabled(True)
		self.figure_ax.clear()
		self.close()

	def clear_window(self, guess_pressure=False):
		self.start_btn.setEnabled(True)
		self.scale_data = []
		self.figure_ax.clear()
		self.canvas.draw()
		self.eta_lb.setText('ETA:  none s')
		self.progress_bar.setValue(0.)
		self.desired_flow = DRAWING_CFG[self.main_window.current_drawing]['desired_flow']
		self.flow_precision = DRAWING_CFG[self.main_window.current_drawing]['flow_precision']
		if guess_pressure and not self.main_window.current_pressure is None:
			self.set_pressure = self.main_window.current_pressure
			self.guess_pressure(self.main_window.current_flow)
		else:
			self.set_pressure = DRAWING_CFG[self.main_window.current_drawing]['init_pressure']
		self.measured_flow = 0.
		self.update_labels()
		
	def update(self):
		self.repaint()
		QtGui.QApplication.processEvents()
	
	def closeEvent(self, event):
		self.main_window.enable_all()
		event.accept()

	def toggle_good_bad(self, bool):
		self.good_btn.setEnabled(bool)
		self.bad_btn.setEnabled(bool)
		
	def launch_worker(self, function, check_func=[], starting_func=[], closing_func=[], toggle_func=None):
		if toggle_func is None:
			def do_nothing(bool):
				return
			enable_func = do_nothing
		else:
			enable_func = toggle_func
		
		enable_func(False)
		
		run = True
		for func in check_func:
			check = func()
			if not check: 
				run = False
				break
		
		if run: 
			for func in starting_func:
				func()
				
			worker = Worker(function)
			worker.signals.finished.connect(lambda: self.worker_finished(closing_func, enable_func))
			worker.signals.update.connect(self.worker_update)
			worker.signals.error.connect(self.worker_error)
			self.thread_pool.start(worker)
			return
		else:
			enable_func(True)
	
	def worker_update(self, upd_list):
		#print('update worker '+str(upd_list[0]))
		self.progress_bar.setValue(upd_list[0])
		self.eta_lb.setText('ETA: {:5.1f} s'.format(upd_list[1]))
		self.scale_data = upd_list[2]
		self.plot_data()

	def worker_finished(self, func_list, enable_func):
		enable_func(True)
		for func in func_list:
			func()
	
	def worker_error(self, type_str, message):
		QtGui.QMessageBox.warning(
						self, 
						'Error: '+type_str, 
						message,
						QtGui.QMessageBox.Ok
						)


class test_window(QtGui.QWidget):
	'''
	Test window to run the given test object.
	- set test variables
	- do test.run()
	- show test progress (progressbar, plot)
	'''
	def __init__(self, main_window, pix_w=700, pix_h=500, parent=None):
		print('test window')
		super(test_window, self).__init__(parent)
		self.setWindowTitle("GLUI: test window")
		self.setWindowIcon(QtGui.QIcon('images/GLUI_logo.png'))
		self.setPalette(PALETTE)
		
		self.setGeometry(50, 50, pix_w, pix_h)
		self.main_window = main_window
		self.set_test()
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		self.thread_pool = QtCore.QThreadPool()
		
		# Start button 
		self.start_btn = QtGui.QPushButton('Start')
		self.start_btn.clicked.connect(self.run_test)
		self.start_btn.setEnabled(True)
		self.grid.addWidget(self.start_btn, 3, 0)
		
		# Reset button 
		self.reset_btn = QtGui.QPushButton('Reset')
		self.reset_btn.clicked.connect(self.set_test_var)
		self.reset_btn.setEnabled(True)
		self.grid.addWidget(self.reset_btn, 3, 1)
		
		
		
	def set_test(self, test_obj=None):
		if test_obj is None: test_obj = Test(self, self.main_window)
		self.test = test_obj
		
	def run_test(self):
		self.test.run()
		
	def set_test_var(self):
		self.test.set_var()
		
		
class inspect_window(QtGui.QWidget):
	def __init__(self, main_window, pix_w=600, pix_h=500, parent=None):
		print('inspect window')
		super(inspect_window, self).__init__(parent)
		self.setWindowTitle("GLUI: inspect")
		self.setWindowIcon(QtGui.QIcon('images/GLUI_logo.png'))
		self.setPalette(PALETTE)
		
		self.setGeometry(50, 50, pix_w, pix_h)
		self.main_window = main_window
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		self.thread_pool = QtCore.QThreadPool()
		
		self.webcam = main_window.webcam
		#self.webcam = cv2.VideoCapture(2)
		#self.webcam = cv2.VideoCapture(1)
		#self.webcam_HD = cv2.VideoCapture(1)
		#self.webcam_HD.set(3,1280)#3280
		#self.webcam_HD.set(4,1024)#2464
		#self.webcam_HD.set(3,3280)
		#self.webcam_HD.set(4,2464)
		
		# NO HD atm
		#self.webcam.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
		#self.webcam.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
		#print('webcam width: '+str(self.webcam.get(3) ))
		#print('webcam heigth: '+str(self.webcam.get(4) ))
		#self.webcam.set(3,1280)
		#self.webcam.set(4,1024)
		self.pix_w = int(self.webcam.get(3))
		self.pix_h = int(self.webcam.get(4))
		
		# Webcam stuff
		self.stream_fps = 24 
		self.stream_lb = QtGui.QLabel()
		self.grid.addWidget(self.stream_lb, 0, 0, 1, 8)
		
		self.picture_btn = QtGui.QPushButton('Save')
		self.picture_btn.clicked.connect(
		lambda: self.launch_worker(
				self.take_and_save_picture,
				toggle_func = self.toggle_move,
				starting_func=[lambda: self.end_stream()], 
				closing_func=[lambda: self.start_stream()]
				)
			)
		self.grid.addWidget(self.picture_btn, 3, 7, 1, 1)
		
		self.save_tag = QtGui.QLineEdit()
		self.save_tag.setText('picture')
		self.grid.addWidget(self.save_tag, 3, 6, 1, 1)
		self.save_tag_lb = QtGui.QLabel('Picture name tag:')
		self.save_tag_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.save_tag_lb, 3, 4, 1, 2)
		
		
		# Absolute move 
		self.abs_mv_lb = QtGui.QLabel('Absolute move [mm]:')
		self.x_lb = QtGui.QLabel('x')
		self.y_lb = QtGui.QLabel('y')
		self.z_lb = QtGui.QLabel('z')
		self.x_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.y_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.z_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.abs_mv_lb, 1, 0)
		self.grid.addWidget(self.x_lb, 1, 1)
		self.grid.addWidget(self.y_lb, 1, 3)
		self.grid.addWidget(self.z_lb, 1, 5)
		
		self.x_in = QtGui.QLineEdit()
		self.y_in = QtGui.QLineEdit()
		self.z_in = QtGui.QLineEdit()
		self.grid.addWidget(self.x_in, 1, 2)
		self.grid.addWidget(self.y_in, 1, 4)
		self.grid.addWidget(self.z_in, 1, 6)
		#self.load_current_position()
		
		self.move_btn = QtGui.QPushButton('Move')
		self.move_btn.clicked.connect(
			lambda: self.launch_worker(
				self.move,
				toggle_func = self.toggle_move,
				check_func = [self.main_window.init_warning]
				#starting_func = [self.load_machine]
				)
			)
		self.grid.addWidget(self.move_btn, 1, 7, 1, 1) 
		
		# Relative move 
		self.rel_mv_lb = QtGui.QLabel('Relative move [mm]:')
		self.dx_lb = QtGui.QLabel('dx')
		self.dy_lb = QtGui.QLabel('dy')
		self.dz_lb = QtGui.QLabel('dz')
		self.dx_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.dy_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.dz_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.rel_mv_lb, 2, 0)
		self.grid.addWidget(self.dx_lb, 2, 1)
		self.grid.addWidget(self.dy_lb, 2, 3)
		self.grid.addWidget(self.dz_lb, 2, 5)
		
		self.dx_in = QtGui.QLineEdit()
		self.dy_in = QtGui.QLineEdit()
		self.dz_in = QtGui.QLineEdit()
		self.grid.addWidget(self.dx_in, 2, 2)
		self.grid.addWidget(self.dy_in, 2, 4)
		self.grid.addWidget(self.dz_in, 2, 6)
		self.load_current_position()
		
		self.rel_move_btn = QtGui.QPushButton('Move')
		self.rel_move_btn.clicked.connect(
			lambda: self.launch_worker(
				lambda: self.move(True),
				toggle_func = self.toggle_move,
				check_func = [self.main_window.init_warning]
				#starting_func = [self.load_machine]
				)
			)
		self.grid.addWidget(self.rel_move_btn, 2, 7, 1, 1)
		
		
		
		
	# Move functions
	def move_xyz(self, x, y, z):
		self.main_window.machine.gotoxyz(x, y, z)
		
	def move_xyz_rel(self, dx, dy, dz):
		curr_x, curr_y, curr_z = self.get_current_position()
		self.main_window.machine.gotoxyz(curr_x + dx, curr_y + dy, curr_z + dz)

	def get_current_position(self):
		if self.main_window.machine is not None:
			x = self.main_window.machine.x
			y = self.main_window.machine.y
			z = self.main_window.machine.z
		else:
			x = None
			y = None
			z = None
		return x, y, z
		
	def load_current_position(self):
		#if self.main_window.machine is not None:		
		#	self.x_in.setText(str(self.main_window.machine.x))
		#	self.y_in.setText(str(self.main_window.machine.y))
		#	self.z_in.setText(str(self.main_window.machine.z))
		self.dx_in.setText(str(0))
		self.dy_in.setText(str(0))
		self.dz_in.setText(str(0))

		x, y, z = self.get_current_position()
		self.x_in.setText(str(x))
		self.y_in.setText(str(y))
		self.z_in.setText(str(z))
		
	def read_xyz_input(self, rel):
		if not rel:
			x_cand = self.x_in.text()
			y_cand = self.y_in.text()
			z_cand = self.z_in.text()
		else:
			x_cand = self.dx_in.text()
			y_cand = self.dy_in.text()
			z_cand = self.dz_in.text()
		try:
			x = float(x_cand)
		except:
			raise ValueError('Could not convert X input to float')
		try:
			y = float(y_cand)
		except:
			raise ValueError('Could not convert Y input to float')
		try:
			z = float(z_cand)
		except:
			raise ValueError('Could not convert Z input to float')
		return x, y, z

	def move(self, rel=False):
		x, y, z = self.read_xyz_input(rel)
		#print('Move to '+str(x)+', '+str(y)+', '+str(z))
		if not rel: self.move_xyz(x, y, z)
		else: self.move_xyz_rel(x, y, z)
		self.load_current_position()
	
				
	# Webcam functions
	def take_picture(self):
		#print('Taking pic')
		attempt = 0
		success = False
		while not success and attempt < 10:
			success, image = self.webcam.read()
			if not success: time.sleep(0.5)
			attempt += 1
		image_r = cv2.rotate(image, cv2.ROTATE_180)
		#image.rotate(180)
		return image_r
	
	def red_cross(self, image):
		center_x = int(self.pix_w/2.)
		center_y = int(self.pix_h/2.)
		length = 10
		thickness = 2
		color = (0, 0, 255) #BGR color
		cv2.line(image, (center_x, center_y - length), (center_x, center_y + length), color, thickness)
		cv2.line(image, (center_x - length, center_y), (center_x + length, center_y), color, thickness)
		
		
	def embed_picture(self, image):
		self.red_cross(image)
		cv2.cvtColor(image, cv2.COLOR_BGR2RGB, image)
		img = QtGui.QImage(image, image.shape[1], image.shape[0], QtGui.QImage.Format_RGB888)
		#print(image.shape)
		#img = QtGui.QImage(image, image.shape[1], image.shape[0], QImage.Format_Indexed8)
		pix = QtGui.QPixmap.fromImage(img)
		self.stream_lb.setPixmap(pix)

	def read_save_tag(self):
		return str(self.save_tag.text())
	
	def save_picture(self, image, path):
		ts = time.time()
		time_str = datetime.datetime.now().strftime("%Y_%b_%d_at_%H_%M_%S")
		x, y, z = self.get_current_position()
		x_str = str(x)
		y_str = str(y)
		z_str = str(z)
		pic_name = self.read_save_tag()+'_x_'+x_str+'_y_'+y_str+'_z_'+z_str+'_'+time_str+'.png'
		print(pic_name)
		cv2.imwrite(path+pic_name, image)
		
	def set_HD(self, on=True):
		if on:
			#sucess1 = self.webcam.set(3,3264)
			#succes2 = self.webcam.set(4,2448)
			sucess1 = self.webcam.set(3,3280)
			succes2 = self.webcam.set(4,2464)
		else:
			self.webcam.set(3,640)
			self.webcam.set(4,480)
		
	def update_stream(self):
		image = self.take_picture()
		self.embed_picture(image)
		
	def start_stream(self):
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update_stream)
		self.timer.start(1000./self.stream_fps)
		
	def end_stream(self):
		self.timer.stop()
		#print('Stream ended')
	
	def take_and_save_picture(self):
		#self.end_stream()
		self.set_HD(True)
		#time.sleep(2)
		image_tmp = self.take_picture()
		image_tmp2 = self.take_picture()
		image = self.take_picture()
		self.set_HD(False)
		#self.start_stream()
		
		#path = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue-no-timeout\\images\\webcam\\'
		#path += datetime.datetime.now().strftime("%Y_%b_%d") + '\\'
		## Make day folder if not there yet
		#if not os.path.isdir(path): os.mkdir(path)
		path = self.main_window.get_picture_path()
		
		self.save_picture(image, path)

	# Widget functions
	def closeEvent(self, event):
		self.end_stream()
		event.accept()
		
	def launch_worker(self, function, check_func=[], starting_func=[], closing_func=[], toggle_func=None):
		if toggle_func is None:
			def do_nothing(bool):
				return
			enable_func = do_nothing
		else:
			enable_func = toggle_func
		
		enable_func(False)
		
		run = True
		for func in check_func:
			check = func()
			if not check: 
				run = False
				break
		
		if run: 
			for func in starting_func:
				func()
				
			worker = Worker(function)
			worker.signals.finished.connect(lambda: self.worker_finished(closing_func, enable_func))
			worker.signals.error.connect(self.worker_error)
			self.thread_pool.start(worker)
			return
		else:
			enable_func(True)

	def worker_finished(self, func_list, enable_func):
		enable_func(True)
		for func in func_list:
			func()
	
	def worker_error(self, type_str, message):
		QtGui.QMessageBox.warning(
						self, 
						'Error: '+type_str, 
						message,
						QtGui.QMessageBox.Ok
						)

	def toggle_move(self, bool):
		self.move_btn.setEnabled(bool)
		self.rel_move_btn.setEnabled(bool)
		self.picture_btn.setEnabled(bool)
		
class scale_window(QtGui.QWidget):
	def __init__(self, main_window, pix_w=700, pix_h=500, parent=None):
		print('scale window')
		super(scale_window, self).__init__(parent)
		self.setWindowTitle("GLUI: scale")
		self.setWindowIcon(QtGui.QIcon('images/GLUI_logo.png'))
		self.setPalette(PALETTE)
		
		self.setGeometry(50, 50, pix_w, pix_h)
		self.main_window = main_window
		
		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		self.thread_pool = QtCore.QThreadPool()
		
		# Mass stuff
		self.mass_record = []
		self.record_length = 120 #in seconds
		
		self.stream_fps = 5 
		self.current_lb = QtGui.QLabel('Current [mg]:')
		self.current_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.current_lb, 1, 0, 1, 2)
		self.current_v_lb = QtGui.QLabel('')
		self.current_a_lb = QtGui.QLabel('')
		self.current_s_lb = QtGui.QLabel('')
		self.update_labels()
		self.grid.addWidget(self.current_v_lb, 1, 2, 1, 2)
		self.grid.addWidget(self.current_a_lb, 1, 4, 1, 2)
		self.grid.addWidget(self.current_s_lb, 1, 6, 1, 2)
		
		# self.save_tag = QtGui.QLineEdit()
		# self.save_tag.setText('picture')
		# self.grid.addWidget(self.save_tag, 3, 6, 1, 1)
		# self.save_tag_lb = QtGui.QLabel('Picture name tag:')
		# self.save_tag_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		# self.grid.addWidget(self.save_tag_lb, 3, 4, 1, 2)
		
		# Plot
		self.figure, self.figure_ax = plt.subplots() 
		self.figure_ax.set(xlabel='time (s)', ylabel='mass (g)', title='')
		self.canvas = Canvas(self.figure)
		self.grid.addWidget(self.canvas, 0, 0, 1, 8)
		
		# Zero button
		self.zero_btn = QtGui.QPushButton('Zero')
		self.zero_btn.clicked.connect(
			lambda: self.launch_worker(
					self.zero_scale,
					toggle_func = self.toggle_all,
					#starting_func=[lambda: self.end_stream()], 
					#closing_func=[lambda: self.start_stream()]
				)
			)
		self.grid.addWidget(self.zero_btn, 2, 2, 1, 1)
		
		# Cal button
		self.calb_btn = QtGui.QPushButton('Calibrate')
		self.calb_btn.clicked.connect(
			lambda: self.launch_worker(
					self.calibrate_scale,
					toggle_func = self.toggle_all,
					#starting_func=[lambda: self.end_stream()], 
					#closing_func=[lambda: self.start_stream()]
				)
			)
		self.grid.addWidget(self.calb_btn, 2, 3, 1, 1)
		
		# Send command
		self.cmd_btn = QtGui.QPushButton('Send')
		self.cmd_btn.clicked.connect(
		lambda: self.launch_worker(
				self.send_command,
				toggle_func = self.toggle_all,
				#starting_func=[lambda: self.end_stream()], 
				#closing_func=[lambda: self.start_stream()]
				)
			)
		self.grid.addWidget(self.cmd_btn, 2, 7, 1, 1)
		
		self.cmd_line = QtGui.QLineEdit()
		self.cmd_line.setText('')
		self.grid.addWidget(self.cmd_line, 2, 5, 1, 2)
		self.cmd_lb = QtGui.QLabel('Scale commands:')
		self.cmd_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.cmd_lb, 2, 0, 1, 2)
		
		# Recording 
		self.rec_lb = QtGui.QLabel('Record :')
		self.rec_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.rec_lb, 3, 0, 1, 2)
		self.rec_sb = QtGui.QSpinBox()
		self.grid.addWidget(self.rec_sb, 3, 2, 1, 1)
		self.rec_sb_lb = QtGui.QLabel('seconds')
		self.grid.addWidget(self.rec_sb_lb, 3, 3, 1, 1)
		self.rec_line = QtGui.QLineEdit()
		self.rec_line.setText('FileName (txt)')
		self.grid.addWidget(self.rec_line, 3, 5, 1, 2)
		self.rec_btn = QtGui.QPushButton('Record')
		self.rec_btn.clicked.connect(
			lambda: self.launch_worker(
					self.record,
					toggle_func = self.toggle_all,
					#starting_func=[lambda: self.end_stream()], 
					#closing_func=[lambda: self.start_stream()]
					)
				)
		self.grid.addWidget(self.rec_btn, 3, 7, 1, 1)
		
		# Clear button
		self.clear_lb = QtGui.QLabel('Clear plot')
		self.clear_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
		self.grid.addWidget(self.clear_lb, 4, 0, 1, 1)
		self.clear_btn = QtGui.QPushButton('Clear')
		self.clear_btn.clicked.connect(
			lambda: self.launch_worker(
					self.clear_data,
					toggle_func = self.toggle_all,
					#starting_func=[lambda: self.end_stream()], 
					#closing_func=[lambda: self.start_stream()]
					)
				)
		self.grid.addWidget(self.clear_btn, 4, 1, 1, 1)

# Button handling
	def toggle_all(self, bool):
		self.rec_btn.setEnabled(bool)
		self.zero_btn.setEnabled(bool)
		self.calb_btn.setEnabled(bool)
		self.cmd_btn.setEnabled(bool)
		
	def enable_all(self):
		self.toggle_all(True)
		
	def disable_all(self):
		self.toggle_all(False)
	
	def send_command(self):
		cmd = str(self.cmd_line.text())
		self.command_scale(cmd)
		
	def record(self):
		duration = int(self.rec_sb.value())
		data = self.record_scale(duration)
		self.write_record(data)
			
	def write_record(self, data):
		file_name = str(self.rec_line.text())
		if not file_name.endswith('.txt'): file_name += '.txt'
		
		path = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue-no-timeout\\scale\\'
		path += datetime.datetime.now().strftime("%Y_%b_%d") + '\\'
		
		# Make day folder if not there yet
		if not os.path.isdir(path): os.mkdir(path)
		
		file_path = path + file_name
		o_file = open(file_path, 'a')
		
		o_file.write('__GUI_RECORD_SESSION__\n')
		o_file.write('time of writing: '+ datetime.datetime.now().strftime("%H:%M:%S") + '\n')
		o_file.write('recorded time  : '+ str(data[-1][0] - data[0][0]) + ' seconds \n')
		
		log = '{:>13}\t{:>7}\t{:>7}\t{:>7}'.format('time', 'value', 'avg', 'sigma')
		o_file.write('_'*(len(log)+2) + '\n')
		o_file.write(log + '\n')
		mass = []
		mass_avg = []
		mass_sig = []
		time_y = []
		for point in data:
			mass.append(point[1][0])
			mass_avg.append(point[1][1])
			mass_sig.append(point[1][2])
			time_y.append(point[0])
			log = '{:13.2f}\t{:7.3f}\t{:7.3f}\t{:7.3f}'.format(point[0], point[1][0], point[1][1], point[1][2])
			o_file.write(log+'\n')
		
		o_file.write('_'*(len(log)+2) + '\n')
		o_file.write('Max :\t\t{:7.3f}\t{:7.3f}\t{:7.3f}\n'.format(max(mass), max(mass_avg), max(mass_sig)))
		o_file.write('Min :\t\t{:7.3f}\t{:7.3f}\t{:7.3f}\n'.format(min(mass), min(mass_avg), min(mass_sig)))
		o_file.write('Mean:\t\t{:7.3f}\t{:7.3f}\t{:7.3f}\n'.format(mean(mass), mean(mass_avg), mean(mass_sig)))
		o_file.write('stdD:\t\t{:7.3f}\t{:7.3f}\t{:7.3f}\n'.format(StdDev(mass), StdDev(mass_avg), StdDev(mass_sig)))
		
		o_file.close()
		
# Stream handling		
	def update_stream(self):
		mass_vector = self.main_window.scale.read_port_h()
		time_stamp = time.time()
		self.update_mass_record(time_stamp, mass_vector)
		self.display_mass()
	
	def start_stream(self):
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.update_stream)
		self.timer.start(1000./self.stream_fps)
		
	def end_stream(self):
		self.timer.stop()

# Mass handling		
	def update_mass_record(self, time_stamp, mass_vector):
		tuple = (time_stamp, mass_vector)
		self.mass_record.append(tuple)
		
		while abs(self.mass_record[0][0] - time_stamp) > self.record_length:
		    del self.mass_record[0]
			
	def update_labels(self):
		#sigma = str(u'\u03C3')
		#mu = str(u'\u03BC')
		#sigma = 'σ'
		#mu = 'μ'
		sigma = 'error'
		mu = 'mean'
		try:
			curr_mass_str_v = str(int(self.mass_record[-1][1][0]*1000))
			curr_mass_str_a = str(int(self.mass_record[-1][1][1]*1000))
			curr_mass_str_s = str(int(self.mass_record[-1][1][2]*1000))
		except:
			curr_mass_str_v = 'None'
			curr_mass_str_a = 'None'
			curr_mass_str_s = 'None'
		self.current_v_lb.setText('{:>5}'.format(curr_mass_str_v))
		self.current_a_lb.setText('{} {:>5}'.format(mu, curr_mass_str_a))
		self.current_s_lb.setText('{} {:>5}'.format(sigma, curr_mass_str_s))
			
	def display_mass(self):
		self.update_labels()

		mass_vec = []
		time_vec = []
		avg_mass_vec = []
		for idx,_ in enumerate(self.mass_record):
			if self.mass_record[idx][1][0] is None:
				mass_vec.append(float('nan'))
				avg_mass_vec.append(float('nan'))
			else:
				mass_vec.append(self.mass_record[idx][1][0]*1000.)
				avg_mass_vec.append(self.mass_record[idx][1][1]*1000.)
			time_vec.append(self.mass_record[idx][0] - self.mass_record[-1][0])
			
		
		self.figure_ax.clear()
		self.figure_ax.plot(time_vec, avg_mass_vec)
		self.figure_ax.set(xlabel='time (s)', ylabel='mass (mg)', title='')
		self.canvas.draw()
		
	def clear_data(self):
		self.mass_record = []
		
# Scale functions
	def zero_scale(self):
		self.main_window.scale.zero()
		
	def calibrate_scale(self):
		self.main_window.scale.calibrate()
		
	def command_scale(self, cmd):
		self.main_window.scale.send_command(cmd)
		
	def record_scale(self, duration):
		data = self.main_window.scale.read_out_time(duration, display=False, record=True)
		return data
		
# Widget functions
	def closeEvent(self, event):
		self.end_stream()
		event.accept()
	
	def launch_worker(self, function, check_func=[], starting_func=[], closing_func=[], toggle_func=None):
		if toggle_func is None:
			def do_nothing(bool):
				return
			enable_func = do_nothing
		else:
			enable_func = toggle_func
		
		enable_func(False)
		
		run = True
		for func in check_func:
			check = func()
			if not check: 
				run = False
				break
		
		if run: 
			for func in starting_func:
				func()
				
			worker = Worker(function)
			worker.signals.finished.connect(lambda: self.worker_finished(closing_func, enable_func))
			worker.signals.error.connect(self.worker_error)
			self.thread_pool.start(worker)
			return
		else:
			enable_func(True)

	def worker_finished(self, func_list, enable_func):
		enable_func(True)
		for func in func_list:
			func()
	
	def worker_error(self, type_str, message):
		QtGui.QMessageBox.warning(
						self, 
						'Error: '+type_str, 
						message,
						QtGui.QMessageBox.Ok
						)
		
		
class WorkerSignals(QtCore.QObject):
	finished = QtCore.pyqtSignal()
	error    = QtCore.pyqtSignal(str, str)
	update   = QtCore.pyqtSignal(list)

class Worker(QtCore.QRunnable):
	def __init__(self, function):
		print('init worker')
		super(Worker, self).__init__()
		self.signals = WorkerSignals()
		self.function = function

	def run(self):
		print('run worker')
		try:
			self.function()
		except TypeError as ex:
			print(ex)
			traceback.print_exc()
			try:
				self.function(self.signals.update)
			except Exception, exp:
				exc_type, exc_obj, exc_tb = sys.exc_info()
				fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
				type_str = str(type(exp)).split('.')[-1].replace('\'>', '')
				traceback.print_exc()
				self.signals.error.emit(type_str, str(exp))
			
		except Exception, exp:
			exc_type, exc_obj, exc_tb = sys.exc_info()
			fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
			type_str = str(type(exp)).split('.')[-1].replace('\'>', '')
			traceback.print_exc()
			self.signals.error.emit(type_str, str(exp))
		self.signals.finished.emit()
		
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	GUI = GLUI(app)
	sys.exit(app.exec_())
	