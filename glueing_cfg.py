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
		'bend_file': 'cache/NeedleBendVar_blue_metal.txt',
		'layer': 'kapton',
		'mass' : 12.,
		'desired_flow':   0.8,
		'flow_precision': 0.5,
		'init_pressure': 1100,
		'above': 0.3,
		'is_encap': False,
	},
	'water_kapton' : {
		'file' : 'drawings/kapton_pigtail.dxf',
		'bend_file': 'cache/NeedleBendVar_blue_metal.txt',
		'layer': 'kapton',
		'mass' : 120.,
		'desired_flow':   20.,
		'flow_precision': 5,
		'init_pressure': 110,
		'above': 0.3,
		'is_encap': False,
	},
	'pigtail_top' : {
		#'file' : 'drawings/kapton_pigtail.dxf',
		'file' : 'drawings/kapton_pigtail_flip.dxf',
		'bend_file': 'cache/NeedleBendVar_blue_metal.txt',
		'layer': 'pigtail_top',
		'mass' : 0.1,
		'desired_flow': 0.3,
		'flow_precision': 0.2,
		'init_pressure': 650,
		'above': 0.15,
		'is_encap': False,
	},
	'pigtail_bot' : {
		#'file' : 'drawings/kapton_pigtail.dxf',
		'file' : 'drawings/kapton_pigtail_flip.dxf', #4.81 up
		'bend_file': 'cache/NeedleBendVar_blue_metal.txt',
		'layer': 'pigtail_bot',
		'mass' : 0.12,
		'desired_flow': 0.3,
		'flow_precision': 0.2,
		'init_pressure': 650,
		'above': 0.15,
		'is_encap': False,
	},
	'pigtail_bot_encap' : {
		'file' : 'drawings/kapton_pigtail.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'pigtail_bot_encap',
		'mass' : 1.5,
		'desired_flow': 10.,
		'flow_precision': 0.5,
		'init_pressure': 2500,
		'above': 0.6,
		'is_encap': True,
	},
	'hybrid_encap' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap',
		'mass' : 240.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 1000,
		'above': 2.5,
		'is_encap': True,
	},
	'hybrid_encap2' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap2',
		'mass' : 240.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 665,
		'above': 2.5,
		'is_encap': True,
	},
	'hybrid_encap3' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap3',
		'mass' : 50.,
		'desired_flow':  1.27564142925,
		'flow_precision': 0.5,
		'init_pressure': 800,
		'above': 2.5,
		'is_encap': True,
	},
	'hybrid_encap4' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap4',
		'mass' : 5.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 1000,
		'above': 1.,
		'is_encap': True,
	},
	'spiral_7l' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap5',
		'mass' : 400.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 650,
		'above': 2.5,
		'is_encap': True,
	},
	'spiral_9' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap6',
		'mass' : 400.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 800,
		'above': 2.5,
		'is_encap': True,
	},
	'ladder_0.7' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap7',
		'mass' : 450.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 800,
		'above': 1.5,
		'is_encap': True,
	},
	'ladder_0.5' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap8',
		'mass' : 400.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 800,
		'above': 1.5,
		'is_encap': True,
	},
	'ladder_0.6' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap9',
		'mass' : 400.,
		'desired_flow': 1.7,
		'flow_precision': 0.5,
		'init_pressure': 800,
		'above': 1.5,
		'is_encap': True,
	},
	'maze' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap_maze',
		'mass' : 400.,
		'desired_flow': 1.4,
		'flow_precision': 0.3,
		'init_pressure': 800,
		'above': 1.1,
		'is_encap': True,
	},
	'block' : {
		'file' : 'drawings/hybrid_encapsulation.dxf',
		'bend_file': 'cache/NeedleBendVar_pink_metal.txt',
		'layer': 'hybrid_encap_block',
		'mass' : 450.,
		'desired_flow': 1.4,
		'flow_precision': 0.3,
		'init_pressure': 1600,
		'above': 1.1,
		'is_encap': True,
	},
}



JIG_CFG = {
	'kapton_A':{
		'offsets' : {
			'coordinate_origin' : [26, 105],#[80, 110],
			'drawing_position' : [35.25, 12.5],
			'jig_hight': 15,
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y+',
			'dx':       135, 
			'dy':       100,  
			'dth':      1, 
			'prb_h':    0.75,
			'jig_file': 'cache/kapton_jig_coo.py'
		},
		'tilt': {
			'p1': [10, -5],
			'p2': [150, -5],
			'p3': [10, 120],
			'max_height': 6,
		},
		#'flow': {
		#	'desired_flow': 10,
		#},
		'drawing': {
			'hight': 5.1, #5 +/-0.1 
			#'file' : 'kapton_pigtail.dxf',
		},
	},
	'kapton_B':{
		'offsets' : {
			'coordinate_origin' : [26, 95],#[36, 110],
			'drawing_position' : [36.5, 28],#[1.25, 0], #[2.25, 3]
			'jig_hight': 15,
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y-',
			'dx':       100, 
			'dy':       115,  
			'dth':      1,  
			'prb_h':    0.75,
			'jig_file': 'cache/kapton_B_jig_coo.py'
		},
		'tilt': {
			'p1': [20, 20],#[0, -5]
			'p2': [130, 20],#[100, -10]
			'p3': [20, 120],#[-10, 85]
			'max_height': 6,
		},
		'flow': {
			'desired_flow': 1,
		},
		'drawing': {
			# 0.410 cloth thickness 0.32 sensor => 0.730 + 0.3 => 1.03
			# 0.732 plexiglass => 1.142 => 1.442
			'hight': 0.5, #Glass + cloth + vacuum #0.8, #Plexi + cloth + vacuum, #0.78,   #1.190,#1.090,           #0.912,#1.012, # 0.712 + 0.3
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
			'coordinate_origin' : [10, 85],
			'drawing_position' : [24, 25.5],#Dark green jig [24.5, 24.5],
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
}

GRID_CFG = {
	'2x2': {
		1: [0, 0],
		2: [0, 150],
		3: [150, 150],
		4: [150, 0],
		'coo_file': 'cache/coordinates_2x2.py',
	},
	'1x1': {
		1: [0, 0],
		'coo_file': 'cache/coordinates_1x1.py',
	},
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