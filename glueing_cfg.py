BOARDS_CFG = {
    # offset: {board nr: [x[mm], y[mm]]}
    'offsets' : {'1': [89.5, 108.5]},
    # hight: z[mm]
    'hight_1' : 20,
	'hight_2' : 15,
}

ST_CFG = {
    # offset: [x[mm], y[mm]]
    'offset' : [75, 100],
    # hight: z[mm]
    'hight' : 20,
	'speed' : {
    	# line nr: mm/min
    	1: 2000,
    	2: 1600,
    	3: 1200,
    	4: 800,
    	5: 400,
	},
	'pressure' : {
    	# line nr: mbar
    	1: 100,
    	2: 200,
    	3: 300,
    	4: 400,
    	5: 500,
	}
}

JIG_OFFSET_CFG = {
	"kapton" : [35.25, 11.75],
	"sensor" : [3.25, 11 ],
	# offset: [x[mm], y[mm]]  (TO BE DETERMINED??)
	# tilt map origin: [x[mm], y[mm]]  !!TO BE DETERMINED!!
	#"tilt_og" : [89.5, 108.5],
	# measure tilt map shifts: [x[mm], y[mm]]  !!TO BE DETERMINED!!
	#"tilt_up" : [10, 10],
}

CALIBRATION_CFG = {
	# offset: [x[mm], y[mm]]  !!TO BE DETERMINED!!
	"offset" : [75, 100],
	# tilt map origin: [x[mm], y[mm]]  !!TO BE DETERMINED!!
	"tilt_og" : [75, 100],
	# measure tilt map shifts: [x[mm], y[mm]]  !!TO BE DETERMINED!!
	"tilt_up" : [10, 10],
}

MIN_OFFSET = [75, 100]
TABLE_HEIGHT = 35

DRAWING_CFG = {
	'kapton' : {
		'file' : 'drawings/kapton_pigtail.dxf',
		'layer': 'kapton',
		'picture_layer' : 'kapton_picture',
		'mass' : 11.,#12.,
		'desired_flow':   0.8,
		'flow_precision': 0.3,
		#'init_pressure': 2000,
		#'init_pressure': 200,
		'init_pressure': 160,
		#'above': 0.3,
		#'above': 0.6,
		#'above': 0.2,
		'above': 0.1,
		'is_encap': False,
		'expected_glue': 'PT601',
	},
	'kapton_short_only' : {
		'file' : 'drawings/kapton_pigtail.dxf',
		'layer': 'kapton_short_only',
		'picture_layer' : 'kapton_picture',
		'mass' : 1.0,#12.,
		'desired_flow':   0.8,
		'flow_precision': 0.3,
		'init_pressure': 160,
		'above': 0.1,
		'is_encap': False,
		'expected_glue': 'PT601',
	},
	'water_kapton' : {
		'file' : 'drawings/kapton_pigtail.dxf',
		'layer': 'kapton',
		'mass' : 120.,
		'desired_flow':   2.,
		'flow_precision': 2.,
		'init_pressure': 50,
		'above': 0.3,
		'is_encap': False,
		'expected_glue': 'WATER',
	},
	'pigtail_U' : {
		'file' : 'drawings/kapton_pigtail_flip.dxf',
		'layer': 'pigtail_top',
		'picture_layer' : 'pigtail_top_picture',
		'mass' : 0.8,
		'desired_flow': 0.3,
		'flow_precision': 0.25,
		'init_pressure': 140,
		#'above': 0.8,#0.3
		'above': 0.15,
		#'above': -0.25,
		'is_encap': False,
		'expected_glue': 'PT601',
	},
	'pigtail_I' : {
		'file' : 'drawings/kapton_pigtail_flip.dxf', 
		'bend_file': 'cache/NeedleBendVar_blue_metal.txt',
		'layer': 'pigtail_bot',
		'picture_layer' : 'pigtail_bot_picture',
		'mass' : 0.3,
		'desired_flow': 0.3,
		'flow_precision': 0.25,
		'init_pressure': 140,
		#'above': 0.8,#0.3,
		'above': 0.05,
		#'above': -0.05,
		'is_encap': False,
		'expected_glue': 'PT601',
	},
	# 'pigtail_bot_encap' : {
		# 'file' : 'drawings/kapton_pigtail.dxf',
		# 'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		# 'layer': 'pigtail_bot_encap',
		# 'mass' : 1.5,
		# 'desired_flow': 10.,
		# 'flow_precision': 0.5,
		# 'init_pressure': 2500,
		# 'above': 0.6,
		# 'is_encap': True,
	# },
	# 'maze' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		# 'layer': 'hybrid_encap_maze',
		# 'mass' : 400.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 800,
		# 'above': 1.1,
		# 'is_encap': True,
	# },
	# 'block' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		# 'layer': 'hybrid_encap_block',
		# 'mass' : 450.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 1600,
		# 'above': 1.1,
		# 'is_encap': True,
	# },
	# 'hybrid_m' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		# 'layer': 'sensor_encap',
		# 'mass' : 800.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 500,
		# 'above': 1.,
		# 'is_encap': True,
	# },
	# 'line' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		# 'layer': 'encap_line',
		# 'mass' : 400.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 500,
		# 'above': 1.2,
		# 'is_encap': True,
	# },
	# 'spiral_5' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		# 'layer': 'spiral_5',
		# 'mass' : 400.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 500,
		# 'above': 1.2,
		# 'is_encap': True,
	# },
	# 'maze_fast' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		# 'layer': 'hybrid_encap_maze',
		# 'mass' : 400.,
		# 'desired_flow': 2.8,
		# 'flow_precision': 0.5,
		# 'init_pressure': 500,
		# 'above': 1.3,
		# 'is_encap': True,
	# },
	# 'hybrid_s5' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'layer': 'sensor_encap_spiral_5',
		# 'mass' : 900.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 200,
		# 'above': 0.9,
		# 'is_encap': True,
	# },
	# 'hybrid_s7' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'layer': 'sensor_encap_spiral_7',
		# 'mass' : 900.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 200,
		# 'above': 0.9,
		# 'is_encap': True,
	# },
	# 'hybrid_s9' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'layer': 'sensor_encap_spiral_9',
		# 'mass' : 900.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 450,
		# 'above': 0.9,#1.3,
		# 'is_encap': True,
	# },
	'encap_s9_L' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'layer': 'sensor_encap_spiral_9_L',
		'picture_layer' : 'encap_L_picture',
		'mass' : 550.,
		'desired_flow': 1.4,
		'flow_precision': 0.3,
		'init_pressure': 450,
		'above': 0.9,#1.3,
		'is_encap': True,
		'expected_glue': 'SY186',
	},
	'encap_s9_R' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'layer': 'sensor_encap_spiral_9_R',
		'picture_layer' : 'encap_R_picture',
		'mass' : 550.,
		'desired_flow': 1.4,
		'flow_precision': 0.3,
		'init_pressure': 450,
		'above': 0.9,#1.3,
		'is_encap': True,
		'expected_glue': 'SY186',
	},
	'encap_s9d_L' : {
		#24 June 2021 FM2
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'layer': 'sensor_encap_spiralD_9_L',
		'picture_layer' : 'encap_L_picture',
		'mass' : 550.,
		'desired_flow': 1.4,
		'flow_precision': 0.3,
		'init_pressure': 450,
		'above': 0.7,#1.3,
		'is_encap': True,
		'expected_glue': 'SY186',
	},
	'encap_s9d_R' : {
		#24 June 2021 FM2
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'layer': 'sensor_encap_spiralD_9_R',
		'picture_layer' : 'encap_R_picture',
		'mass' : 550.,
		'desired_flow': 1.4,
		'flow_precision': 0.3,
		'init_pressure': 450,
		'above': 0.7,#1.3,
		'is_encap': True,
		'expected_glue': 'SY186',
	},
	'FM3_hot_fix' : {
		#24 June 2021 FM2
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'layer': 'FM3_hot_fix',
		'picture_layer' : 'encap_R_picture',
		'mass' : 70.,
		'desired_flow': 1.4,
		'flow_precision': 0.3,
		'init_pressure': 450,
		'above': 0.5,#1.3,
		'is_encap': True,
		'expected_glue': 'SY186',
	},
	# 'hybrid_s9b' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'layer': 'sensor_encap_spiral_9b',
		# 'mass' : 900.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 200,
		# 'above': 0.9,
		# 'is_encap': True,
	# },
	# 'tesy_pcb_s9' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'layer': 'test_pcb_spiral_9',
		# 'mass' : 450.,
		# 'desired_flow': 1.4,
		# 'flow_precision': 0.3,
		# 'init_pressure': 500,
		# 'above': 0.9,
		# 'is_encap': True,
	# },
	# 'hybrid_s9_out' : {
		# 'file' : 'drawings/hybrid_encapsulation.dxf',
		# 'layer': 'sensor_encap_spiral_9_outer',
		# 'mass' : 100.,
		# 'desired_flow': 1.2,
		# 'flow_precision': 0.3,
		# 'init_pressure': 450,
		# 'above': 0.7,#1.3,
		# 'is_encap': True,
	# },
	'kaptonx5' : {
		'file' : 'drawings/kapton_pigtail.dxf',
		'layer': 'kaptonx5',
		'mass' :  50., #60., #90.,#120.,
		'desired_flow':   0.8,
		'flow_precision': 0.3,
		'init_pressure': 2000,
		#'init_pressure': 200,
		#'above': 0.3,
		'above': 0.2,
		'is_encap': False,
		'expected_glue': 'PT601',
	},
}



JIG_CFG = {
	#'kapton_A':{
	'kapton_jig':{
		'offsets' : {
			#'coordinate_origin' : [11, 114], #[11, 104], #[26, 104],
			#'drawing_position' : [33.55, 12.2], #35.25
			#'drawing_position' : [34.1, 12.2],#[33.4, 12.9]
			'drawing_position' : [33.6, 12.7],#[33.2, 13.5], 
			'jig_hight': 15,
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y+',
			'p1': [11, 114],
			'p2': [11+150, 114],
			'p3': [11-12, 114+110],
			#'dx':       150, #135, 
			#'dy':       110, #100,
			'dth':      1, 
			#'prb_h':    0.75,
			#'jig_file': 'cache/kapton_jig_coo.py'
		},
		'tilt': {
			#'p1': [10, -5],
			#'p2': [150, -5],
			#'p3': [10, 120],
			'p1': [37.5, 14],
			'p2': [131, 14],
			'p3': [37.5, 103.5],
			'max_height': 6,
		},
		'drawing': {
			#'hight': 5.1, #5 +/-0.1 
			'hight': 0,
		},
	},
	#'kapton_B':{
	'sensor_jig':{
		'offsets' : {
			#'coordinate_origin' : [26, 98],
			'drawing_position' : [34.3, 28.1],
			'jig_hight': 15,
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y-',
			'p1': [26, 98-8],
			'p2': [26+100, 98-8],
			'p3': [26-30, 98+115],
			#'dx':       100, 
			#'dy':       115,  
			'dth':      1,  
			#'prb_h':    0.75,
			'jig_file': 'cache/kapton_B_jig_coo.py'
		},
		'tilt': {
			#'p1': [20, 20],#[0, -5]
			#'p2': [130, 20],#[100, -10]
			#'p3': [20, 120],#[-10, 85]
			'p1': [40, 33],#[0, -5]
			'p2': [125+6, 33],#[100, -10]
			'p3': [40, 112],#[-10, 85]
			'max_height': 6,
		},
		'flow': {
			'desired_flow': 1,
		},
		'drawing': {
			
			#'hight': 1.16, #Sensor + cloth + vacuum
			'hight': 0, #Sensor + cloth + vacuum
			'file' : 'kapton_pigtail2.dxf',
		},
	},
	'table':{
		'offsets' : {
			'coordinate_origin' : [10, 85],
			'drawing_position' : [0, 0.1],
			'jig_hight': 3,
		},
		'probe': {
			'probe_x':  'x+', 
			'probe_y':  'y+',
			'dx':       98, 
			'dy':       98,  
			'dth':      1,  
			'prb_h':    0.75,
			'jig_file': 'cache/table_jig_coo.py'
		},
		'tilt': {
			'p1': [15, 5],
			'p2': [85, 5],
			'p3': [15, 85],
			'max_height': 6,
		},
		'flow': {
			'desired_flow': 0.5,
		},
		'drawing': {
			'hight': 0., # 0.712 + 0.3
			'file' : 'kapton_pigtail.dxf',
		},
	},
	'hybrid':{
		'offsets' : {
			'coordinate_origin' : [10, 85],
			'drawing_position' : [21.5, 23.75],
			'jig_hight': 3,
		},
		'probe': {
			'probe_x':  'x+', 
			'probe_y':  'y+',
			'dx':       98, 
			'dy':       98,  
			'dth':      1,  
			'prb_h':    0.75,
			'jig_file': 'cache/hybrid_jig_coo.py'
		},
		'tilt': {
			'p1': [15, 5],
			'p2': [85, 5],
			'p3': [15, 85],
			'max_height': 6,
		},
		#'flow': {
		#	'desired_flow': 0.5,
		#},
		'drawing': {
			'hight': 0., # 0.712 + 0.3
		},
	},
	'table_hybrid':{
		'offsets' : {
			#'coordinate_origin' : [10, 85],
			'coordinate_origin' : [-9.84, 70.],
			#'drawing_position' : [21.5, 25.5],#Dark green jig [24.5, 24.5],
			'drawing_position' : [2.1, 10.5],
			'jig_hight': 3,
		},
		'probe': {
			'probe_x':  'x+', 
			'probe_y':  'y+',
			'dx':       98, 
			'dy':       98,  
			'dth':      1,  
			'prb_h':    0.75,
			'jig_file': 'cache/table_jig_coo.py'
		},
		'tilt': {
			# On jig
			# 'p1': [15, 5],
			# 'p2': [85, 5],
			# 'p3': [15, 85],
			# On test PCB
			#'p1': [23, 16],
			#'p2': [115, 16],
			#'p3': [23, 40],
			'p1': [1.36, .24],
			'p2': [95.36, -0.75],
			'p3': [1.36, 22.24],
			'max_height': 6,
		},
		'flow': {
			'desired_flow': 0.5,
		},
		'drawing': {
			'hight': 0., # 0.712 + 0.3
			'file' : 'kapton_pigtail.dxf',
		},
	},
	'carrier_top':{
		'offsets' : {
			'coordinate_origin' : [10, 80],
			## DM2
			#'drawing_position' : [47., 37.2],#[47.65, 36.2],
			# FM 1
			#'drawing_position' : [47.8, 36.2],
			# FM 2
			'drawing_position' : [47.7, 36.2],
			'jig_hight': 25,
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y-',
			'dx':       155, 
			'dy':       150,  
			'dth':      1,  
			'prb_h':    0.75,
		},
		'tilt': {
			## DM 2
			#'p1': [44.6, 35.],     # C35 mark
			#'p2': [151.7, 34.6],    # C34 mark
			#'p3': [45.4, 131.4],    # C34 mark
			# FM 1
			'p1': [41.6, 32.],     # C35 mark
			'p2': [155.7, 31.6],    # C34 mark
			'p3': [42.4, 137.],    # C34 mark
			'max_height': 5,
		},
		'drawing': {
			'hight': 0.,
		},
	},
	#'carrier_bot':{
	#	'offsets' : {
	#		'coordinate_origin' : [10, 80],
	#		'drawing_position' : [46.85, 36.2],
	#		'jig_hight': 14,
	#	},
	#	'probe': {
	#		'probe_x':  'x-', 
	#		'probe_y':  'y-',
	#		'dx':       155, 
	#		'dy':       150,  
	#		'dth':      1,  
	#		'prb_h':    0.75,
	#	},
	#	'tilt': {
	#		# Measures tilt on hybrids
	#		# 'p1': [39, 33],
	#		# 'p2': [156, 35],
	#		# 'p3': [39, 131],
	#		# Right next to bonds
	#		'p1': [42.5, 42],
	#		'p2': [155, 42],
	#		'p3': [42.5, 124],
	#		#'p1': [44.6, 34.8],     # C35 mark
	#		#'p2': [151.5, 34.1],    # C34 mark
	#		#'p3': [45.4, 131.4],    # C34 mark
	#		'max_height': 5,
	#	},
	#	'drawing': {
	#		'hight': 1.,
	#	},
	#},
	'carrier_flip':{
		'offsets' : {
			'coordinate_origin' : [-29.75, 61],
			#Right
			#'drawing_position' : [48.6, 36.3],
			#Left
			#'drawing_position' : [47.5, 36.5],
			# FM3 y 10.6
			'drawing_position' : [47.5, 47.1],
			
			
			'jig_hight': 25,
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y-',
			'dx':       155, 
			'dy':       145,  
			'dth':      1,  
			'prb_h':    0.75,
		},
		'tilt': {
			# Measures tilt on hybrids
			# 'p1': [39, 33],
			# 'p2': [156, 35],
			# 'p3': [39, 131],
			# Right next to bonds
			#'p1': [45.5, 40.5],      # no mark (between bottom pad and bonds)
			#'p2': [155, 41.5],       # A3 mark
			#'p3': [44.7, 127.3],     # A3 mark

			#'p1': [41.6, 37.],     # C35 mark
			#'p2': [155.7, 36.6],   # C34 mark
			#'p3': [41.5, 131.5],    # C34 mark
			
			#FM3 x 1.15+1 y 5.65+1.7
			'p1': [43.75, 44.35],     # C35 mark
			'p2': [156.6, 43.95],   # C34 mark
			'p3': [43.65, 138.85],    # C34 mark
			
			'max_height': 5,
		},
		'drawing': {
			'hight': 0.3,
		},
	},
	'KIT_IsoProp':{
		'offsets' : {
			'coordinate_origin' : [5, 119],
			##'drawing_position' : [33.55, 12.2], #35.25
			'drawing_position' : [23.2, 28.5],#[24, 29],
			'jig_hight': 30,
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y-',
			'dx':       135, 
			'dy':       138,  
			'dth':      1, 
			'prb_h':    0.75,
			##'jig_file': 'cache/kapton_jig_coo.py'
		},
		'tilt': {
			'p1': [15, 20],
			'p2': [120, 20],
			'p3': [15, 120],
			'max_height': 6,
		},
		'drawing': {
			'hight': 4.0, #5 +/-0.1 
		},
		# 'offsets' : {
			# 'coordinate_origin' : [32, 152],
			##'drawing_position' : [33.55, 12.2], #35.25
			# 'drawing_position' : [24, 29],
			# 'jig_hight': 20,
		# },
		# 'probe': {
			# 'probe_x':  'x-', 
			# 'probe_y':  'y-',
			# 'dx':       83, 
			# 'dy':       75,  
			# 'dth':      1, 
			# 'prb_h':    0.75,
			##'jig_file': 'cache/kapton_jig_coo.py'
		# },
		# 'tilt': {
			# 'p1': [27, 33],
			# 'p2': [120, 33],
			# 'p3': [27, 120],
			# 'max_height': 6,
		# },
		# 'drawing': {
			# 'hight': 5., #5 +/-0.1 
		# },
	},
}

GRID_CFG = {
	'2x2': {
		1: [0, 0],
		2: [0, 150],
		3: [150, 150],
		4: [150, 0],
	},
	'1x1': {
		1: [0, 0],
	},
	#'1xn': {1: [0, 0]},
}

FLOW_CFG = {
	'water':{
		'start_pressure': 200,
	},
	'glue': {
		'start_pressure': 4000,
	},
}

def sum_offsets(off1, off2):
	if not isinstance(off1, list) or not isinstance(off2, list): raise ValueError('sum_offsets: offsets must be lists')
	if len(off1) != len(off2): raise ValueError('sum_offsets: offsets not of equal size')
	off = [0]*len(off1)
	for i in range(len(off1)):
		off[i] = off1[i] + off2[i] 
	return off