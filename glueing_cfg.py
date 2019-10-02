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

def sum_offsets(off1, off2):
	if not isinstance(off1, list) or not isinstance(off2, list): raise ValueError('sum_offsets: offsets must be lists')
	if len(off1) != len(off2): raise ValueError('sum_offsets: offsets not of equal size')
	off = [0]*len(off1)
	for i in range(len(off1)):
		off[i] = off1[i] + off2[i] 
	return off