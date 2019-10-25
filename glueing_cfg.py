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
		'file' : 'kapton_pigtail.dxf',
		'layer': 'kapton',
		'mass' : 18.,
	},
	'pigtail_top' : {
		'file' : 'kapton_pigtail.dxf',
		'layer': 'pigtail_top',
		'mass' : 0.01,
	},
	'pigtail_bot' : {
		'file' : 'kapton_pigtail.dxf',
		'layer': 'pigtail_bot',
		'mass' : 0.01,
	},
}


JIG_CFG = {
	'kapton_A':{
		'offsets' : {
			'table_position' : [80, 110],
			'coordinate_origin' : [35.25, 11.75],
		},
		'probe': {
			'probe_x':  'x-', 
			'probe_y':  'y+',
			'dx':       135, 
			'dy':       100,  
			'dth':      1, 
			'prb_h':    0.75,
			'jig_file': 'kapton_jig_coo.py'
		},
		'tilt': {
			'p1': [10, -5],
			'p2': [150, -5],
			'p3': [10, 120],
			'max_height': 6,
		},
		'flow': {
			'desired_flow': 10,
		},
		'drawing': {
			'hight': 5.5, # 5.3 + 0.2
			'file' : 'kapton_pigtail.dxf',
		},
	},
	'kapton_B':{
		'offsets' : {
			'table_position' : [36, 110],
			'coordinate_origin' : [2.25, 2], #[2.25, 3]
			'jig_hight': 15,
		},
		'probe': {
			'probe_x':  'x+', 
			'probe_y':  'y+',
			'dx':       101, 
			'dy':       105,  
			'dth':      1,  
			'prb_h':    0.75,
			'jig_file': 'kapton_B_jig_coo.py'
		},
		'tilt': {
			'p1': [0, -5],
			'p2': [100, -5],
			'p3': [-10, 85],
			'max_height': 6,
		},
		'flow': {
			'desired_flow': 1,
		},
		'drawing': {
			'hight': 1.19,#0.912,#1.012, # 0.712 + 0.3
			'file' : 'kapton_pigtail.dxf',
		},
	},
	'table':{
		'offsets' : {
			'table_position' : [10, 90],
			'coordinate_origin' : [0, 0.1],
			'jig_hight': 3,
		},
		'probe': {
			'probe_x':  'x+', 
			'probe_y':  'y+',
			'dx':       98, 
			'dy':       98,  
			'dth':      1,  
			'prb_h':    0.75,
			'jig_file': 'table_jig_coo.py'
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
			'hight': 0.3, # 0.712 + 0.3
			'file' : 'kapton_pigtail.dxf',
		},
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