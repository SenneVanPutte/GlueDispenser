import sys
import ezdxf
import json
from PyQt4 import QtGui, QtCore
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as Canvas
from glueing_cfg import DRAWING_CFG, JIG_CFG, GRID_CFG
from gcode_handler import gcode_handler, drawing, make_jig_coord_grid, make_quick_func, drawing2, calc_bend
from scale_handler import scale_handler, delay_and_flow_regulation, read_glue_type, load_f_and_p, write_f_and_p

DEFAUL_DRAWING = 'kapton'
DEFAUL_JIG = 'kapton_B'
DEFAUL_GRID = '1x1'
DEFAUL_POS_CAL_IDX = 'all'
DEFAUL_TILT_CAL_IDX = 'all'

class GLUI(QtGui.QWidget):

	def __init__(self):
		super(GLUI, self).__init__()
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
		self.current_drawing = DEFAUL_DRAWING
		draw_dd = QtGui.QComboBox()
		for drawing in DRAWING_CFG:
			draw_dd.addItem(drawing)
		draw_dd.setCurrentIndex(DRAWING_CFG.keys().index(DEFAUL_DRAWING))
		draw_dd.activated[str].connect(self.choose_drawing)
		self.grid.addWidget(draw_dd, 1, 1)
		draw_lb = QtGui.QLabel('Selected Drawing:')
		self.grid.addWidget(draw_lb, 1, 0)
		
		# Jig drop down
		self.current_jig = DEFAUL_JIG
		jig_dd = QtGui.QComboBox()
		for jig in JIG_CFG:
			jig_dd.addItem(jig)
		jig_dd.setCurrentIndex(JIG_CFG.keys().index(DEFAUL_JIG))
		jig_dd.activated[str].connect(self.choose_jig)
		self.grid.addWidget(jig_dd, 2, 1)
		jig_lb = QtGui.QLabel('Selected Jig:')
		self.grid.addWidget(jig_lb, 2, 0)
		
		# Grid drop down
		self.current_grid = DEFAUL_GRID
		grid_dd = QtGui.QComboBox()
		for grid in GRID_CFG:
			grid_dd.addItem(grid)
		grid_dd.setCurrentIndex(GRID_CFG.keys().index(DEFAUL_GRID))
		grid_dd.activated[str].connect(self.choose_grid)
		self.grid.addWidget(grid_dd, 3, 1)
		grid_lb = QtGui.QLabel('Selected Grid:')
		self.grid.addWidget(grid_lb, 3, 0)
		
		# Overview plot
		self.figure_ov = plt.figure(figsize=(10,5))
		self.canvas_ov = Canvas(self.figure_ov)
		self.grid.addWidget(self.canvas_ov, 0, 0, 1, 2)
		self.plot_ov()
		
		
		# Calibrate position button and drop down
		self.pos_cal_idx = DEFAUL_POS_CAL_IDX
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
		self.pos_func_dict = None
		self.load_pos_func_dict()
		self.tilt_cal_idx = DEFAUL_TILT_CAL_IDX
		self.tilt_cal_idx_dd = QtGui.QComboBox()
		self.load_dd_tilt_cal() 
		self.tilt_cal_idx_dd.activated[str].connect(self.choose_tilt_cal_idx)
		self.grid.addWidget(self.tilt_cal_idx_dd, 1, 3)
		
		#tilt_cal_btn = QtGui.QPushButton('Calibrate')
		#tilt_cal_btn.clicked.connect(self.tilt_cal)
		tilt_cal_lb = QtGui.QLabel('Calibrate tilt:')
		self.grid.addWidget(tilt_cal_lb, 1, 2)
		# TODO:
		#x pos_func file for all jig types, now only for all grid
		#x self.pos_func_dict load for all changes (look up file)
		# check self.pos_func_dict to enable drop down elements or tilt button
		
		
		
		# Init machine button
		machine_init_btn = QtGui.QPushButton('Init')
		machine_init_btn.clicked.connect(self.init_machine)
		self.grid.addWidget(machine_init_btn, 4, 4)
		machine_init_lb = QtGui.QLabel('Init LitePlacer:')
		self.grid.addWidget(machine_init_lb, 4, 2)
		
		
		
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
		ax = self.figure_ov.add_subplot(111)
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
		
		coo_f_dict = make_jig_coord_grid(
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
		
	
	def load_dd_pos_cal(self):
		self.pos_cal_idx_dd.clear()
		
		cb_items = ['all']
		for idx in GRID_CFG[self.current_grid]:
			if not isinstance(idx, int): continue
			cb_items.append(str(idx))
		cb_items.sort()
		for idx in range(len(cb_items)):
			self.pos_cal_idx_dd.addItem(cb_items[idx])
		
		self.pos_cal_idx = DEFAUL_POS_CAL_IDX
		def_idx = cb_items.index(str(DEFAUL_POS_CAL_IDX))
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
		
		self.tilt_cal_idx = DEFAUL_TILT_CAL_IDX
		def_idx = cb_items.index(str(DEFAUL_TILT_CAL_IDX))
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
			if unicode(jig) in read_data:
				func_dict[jig] = make_quick_func( 
									sin=read_data[unicode(jig)]['sin'], 
									cos=read_data[unicode(jig)]['cos'], 
									a=read_data[unicode(jig)]['offset_x'], 
									b=read_data[unicode(jig)]['offset_y']
									)
			else: func_dict[jig] = None
		
		self.pos_func_dict = func_dict
		print('self.pos_func_dict', self.pos_func_dict) 
		
	def init_machine(self):
		try:
			self.machine = gcode_handler()
		except:
			print('Machine not made')
			pass
		self.machine.init_code()
		
		

		

if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	GUI = GLUI()
	sys.exit(app.exec_())
	