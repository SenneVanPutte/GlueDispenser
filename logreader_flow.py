import os
import copy
import math
import time
import decimal
import datetime
import calendar
import matplotlib
from matplotlib import pyplot
from scale_handler import lin_reg

LOG_DIR = 'log/'
month_dict = dict((k,v) for v,k in enumerate(calendar.month_abbr))

up_date = '2020_Dec_82'
dn_date = '2019_Oct_23'

# Pink plastic needle
#TS_FROM = 1579005640.29
#TS_TO = 9579005640.29

# ? needle
TS_FROM = 1575555723.
TS_TO = 1579005640.29

#exclusion_list = []
exclusion_list = ['2019_Nov_06', '2019_Nov_08']

def drange(x, y, jump):
  while x < y:
    yield float(x)
    x += jump#x + decimal.Decimal(jump)

def date_to_list(date_str):
	date_splt = date_str.split('_')
	month_num = month_dict[date_splt[1]]
	return [int(date_splt[0]), month_num, int(date_splt[-1])]


def comp_date(date, date_dn, date_up):
	date_n = date_to_list(date)
	date_dn_n = date_to_list(date_dn)
	date_up_n = date_to_list(date_up)
	
	if date_n[0] < date_dn_n[0]: return False
	elif date_n[0] > date_up_n[0]: return False
	
	elif date_n[0] == date_dn_n[0]:
		if date_n[1] < date_dn_n[1]: 
			return False
		elif date_n[1] == date_dn_n[1]:
			if date_n[2] < date_dn_n[2]: return False
			else: return True
		#else: return True
	if date_n[0] == date_up_n[0]:
		if date_n[1] > date_up_n[1]: return False
		elif date_n[1] == date_up_n[1]:
			if date_n[2] > date_up_n[2]: return False
			else: return True
		else: return True
	
	#else: return True
	return True
	
	
	


file_lst = os.listdir(LOG_DIR)
log_lst = []
for fil in file_lst:
	if 'flow' in fil and '.log' in fil: 
		print(fil)
		date_str = fil.replace('flow_', '').replace('.log','')
		print(date_str)
		if comp_date(date_str, dn_date, up_date): 
			if date_str not in exclusion_list:
				print('kept')
				log_lst.append(fil)

		
		#log_lst.append(fil)  
#print(log_lst)

# inp_Time = raw_input('enter Time: ')
# inp_time_splt = inp_Time.split(':')
# now = datetime.datetime.now()
# year = int(inp_time_splt[0])
# month = int(inp_time_splt[1])
# day = int(inp_time_splt[2])
# hour = int(inp_time_splt[3])
# min = int(inp_time_splt[4])
# #ts = calendar.timegm(datetime.datetime(year, month, day, hour, min).timetuple())
# ts = time.mktime(datetime.datetime(year, month, day, hour, min).timetuple())
# print(ts)
# print(time.time())

# Divide data
data = {}
data['PT601'] = {}
data['SY186'] = {}
data['WATER'] = {}

for key in data:
	data[key]['time'] = {}
	data[key]['flow'] = {}
	data[key]['pres'] = {}
	data[key]['relt'] = {}
	data[key]['time']['tot'] = []
	data[key]['flow']['tot'] = []
	data[key]['pres']['tot'] = []
	data[key]['relt']['tot'] = []
	
for log in log_lst:
	date = log.replace('flow_', '').replace('.log', '')
	log_file = open(LOG_DIR+log, 'r')
	lines = log_file.readlines()
	log_file.close()
		
	glue_key = 'PT601'
	ref_ts = 0.
	#print(data)
	for line in lines:
		if '#' in line: 
			splt_line = line.replace('\n', '').split(' ')
			if 'GLUE TYPE' in line: glue_key = splt_line[-1]
			elif 'GLUE TS' in line: ref_ts = float(splt_line[-1])
			continue
		if glue_key not in data: continue
		if date not in data[glue_key]['time']:
			data[glue_key]['time'][date] = []
			data[glue_key]['flow'][date] = []
			data[glue_key]['pres'][date] = []
			data[glue_key]['relt'][date] = []
			#print(data)
	    #if date not in data[glue_key]['time']:
            #    	data[glue_key]['time'][date] = []
		
		line_splt = line.replace('\n', '').split('\t')
		t = float(line_splt[0])
		p = float(line_splt[2])
		f = float(line_splt[4])
		
		if t < TS_FROM: continue
		if t > TS_TO: continue
		
		if f < 0.: continue
		if p > 5600: continue
		
		data[glue_key]['time']['tot'].append(t)
		data[glue_key]['flow']['tot'].append(f)
		data[glue_key]['pres']['tot'].append(p)
		data[glue_key]['relt']['tot'].append((t - ref_ts)/60.)
		
		data[glue_key]['time'][date].append(t)
		data[glue_key]['flow'][date].append(f)
		data[glue_key]['pres'][date].append(p)
		data[glue_key]['relt'][date].append((t - ref_ts)/60.)
	
# Plot
#print(data['SY186'])
#for glue in data:
for glue in ['PT601']:
	if 'WATER' in glue or 'AIR' in glue: continue 
	print(glue)
	#fonp_tot = []
	#for idx in range(len(data[glue]['time']['tot'])):
	#	f = data[glue_key]['flow']['tot'][idx]
	#	p = data[glue_key]['pres']['tot'][idx]
	#	print(f)
	#	print(p)
	#	fonp_tot.append(f/(p/1000.))
	fonp_tot = [data[glue]['flow']['tot'][idx]/(data[glue]['pres']['tot'][idx]/1000.) for idx in range(len(data[glue]['time']['tot']))]
	fonp_tot_log = [math.log(fonp) for fonp in fonp_tot]

	fig, ax = pyplot.subplots() 
	ax.scatter(data[glue]['time']['tot'], fonp_tot, label='measurement')
	ax.set(xlabel='time (s)', ylabel='flow/pressure (mg/s bar)', title=glue)
	pyplot.show()
	
	fonp_dict = {}
	fig, ax = pyplot.subplots() 
	for date in data[glue]['time']:
		if 'tot' in date: continue
		fonp_dict[date] = [data[glue]['flow'][date][idx]/(data[glue]['pres'][date][idx]/1000.) for idx in range(len(data[glue]['time'][date]))]
		ax.scatter(data[glue]['relt'][date], fonp_dict[date], label=date)
	ax.legend(loc='upper right')
	ax.set(xlabel='time (min)', ylabel='flow/pressure (mg/s bar)', title=glue)
	ax.set_yscale('log')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	a, b, a_int, b_int, False = lin_reg(data[glue]['relt']['tot'], fonp_tot_log)
	max_t = max(data[glue]['relt']['tot'])
	min_t = min(data[glue]['relt']['tot'])
	t_step = (max_t - min_t)/200.
	time_sim = list(drange(min_t, max_t + t_step, t_step))#copy.deepcopy(time_tot)
	fonp_sim = [math.exp(a + b*t) for t in time_sim]
	fonp_sim_up = [math.exp(a_int[1] + b_int[1]*t) for t in time_sim]
	fonp_sim_dn = [math.exp(a_int[0] + b_int[0]*t) for t in time_sim]

	#time_sim, fonp_sim = zip(*sorted(zip(time_sim, fonp_sim)))

	ax.scatter(data[glue]['relt']['tot'], fonp_tot, label='data')
	ax.plot(time_sim, fonp_sim, 'r-', label='fit')
	ax.plot(time_sim, fonp_sim_up, 'y-', label='fit up')
	ax.plot(time_sim, fonp_sim_dn, 'y-', label='fit down')
	ax.legend(loc='lower left')
	ax.set(xlabel='time (min)', ylabel='flow/pressure (mg/s bar)', title=glue)
	ax.set_yscale('log')
	pyplot.show()
	
	fig, ax = pyplot.subplots() 
	press_expt_dict = {}
	for date in data[glue]['time']:
		if 'tot' in date: continue
		press_expt_dict[date] = []
		for idx, pres in enumerate(data[glue]['pres'][date]):
			press_expt_dict[date].append(pres*(math.exp(a + b*data[glue]['relt'][date][idx])))
		ax.scatter(press_expt_dict[date], data[glue]['flow'][date], label=date)
	#press_expt = []
	#for idx, pres in enumerate(data[glue]['pres']['tot']):
	#	press_expt.append(pres*(math.exp(a + b*data[glue]['relt']['tot'][idx])))


	#time_sim, fonp_sim = zip(*sorted(zip(time_sim, fonp_sim)))

	#ax.scatter(press_expt, data[glue]['flow']['tot'], label='data')
	ax.legend(loc='lower right')
	ax.set(xlabel='Pressure*exp(a + b*Time) (mbar)', ylabel='flow (mg/s)', title='')
	#ax.set_yscale('log')
	pyplot.show()
	
exit()	
		
	

time_lst = []
flow_lst = []
pres_lst = []
fonp_lst = []

time_dict = {}
flow_dict = {}
pres_dict = {}
fonp_dict = {}
glts_dict = {}
gtyp_dict = {}
for log in log_lst:
	log_file = open(log, 'r')
	lines = log_file.readlines()
	log_file.close()
	
	time_dict[log] = []
	flow_dict[log] = []
	pres_dict[log] = []
	fonp_dict[log] = []
	glts_dict[log] = []
	
	for line in lines:
		
		if '#' in line: 
			if 'GLUE TS' in line:
				line_splt = line.replace('\n', '').replace(' ', '').split(':')
				glts_dict[log].append(float(line_splt[-1]))
			continue 
		
		line_splt = line.replace('\n', '').split('\t')
		
		Time = float(line_splt[0])
		pres = float(line_splt[2])
		flow = float(line_splt[4])
		
		if flow < 0.: continue
		if pres > 5600: continue
		
		time_lst.append(Time)
		pres_lst.append(pres)
		flow_lst.append(flow)
		fonp_lst.append(flow/(pres + 0.))
		
		time_dict[log].append(Time)
		pres_dict[log].append(pres)
		flow_dict[log].append(flow)
		fonp_dict[log].append(flow/(pres/1000. + 0.))
		
		
 
		
fig, ax = pyplot.subplots() 
#ax.scatter(time_lst, flow_lst, label='measurement')
#ax.scatter(pres_lst, flow_lst, label='measurement')
ax.scatter(time_lst, fonp_lst, label='measurement')
#ax.set(xlabel='Time (s)', ylabel='flow (mg/s)', title='')
#ax.set(xlabel='pressure (mbar)', ylabel='flow (mg/s)', title='')
ax.set(xlabel='Time (s)', ylabel='flow/pressure (mg/s mbar)', title='')
pyplot.show()

fig, ax = pyplot.subplots() 
time_tot = []
press_tot = []
flow_tot = []
fonp_tot = []
fonp_tot_log = []

for log in time_dict:
	Time = time_dict[log]
	fonp = fonp_dict[log]
	press = pres_dict[log]
	flow = flow_dict[log]
	
	time_rel = []
	ts = glts_dict[log]
	for t in Time:
		rel_timy = []
		for tsy in ts:
			t_diff = t - tsy
			if t_diff < 0.: continue
			else: rel_timy.append(t_diff)
		if len(rel_timy) == 0: time_rel.append(t - Time[0])
		elif len(rel_timy) == 1: time_rel.append(rel_timy[0])
		else: time_rel.append(min(rel_timy))
	
	time_rel_rs = [t/60. for t in time_rel]
	fonp_log = [math.log(r) for r in fonp]
	
	#time_rel = [(t - Time[0])/60. for t in Time]
	time_tot.extend(time_rel_rs)
	fonp_tot.extend(fonp)
	press_tot.extend(press)
	flow_tot.extend(flow)
	fonp_tot_log.extend(fonp_log)
	
	ax.scatter(time_rel_rs, fonp, label=log)
ax.legend(loc='upper right')
#ax.set_xlim([0, 550])
#ax.set_ylim([0, 2.5])
ax.set(xlabel='Time (min)', ylabel='flow/pressure (mg/s bar)', title='')
ax.set_yscale('log')
pyplot.show()

fig, ax = pyplot.subplots() 
#print(time_tot)
#print(fonp_tot_log)
a, b, a_int, b_int, False = lin_reg(time_tot, fonp_tot_log)

max_t = max(time_tot)
min_t = min(time_tot)
t_step = (max_t - min_t)/200.
time_sim = list(drange(min_t, max_t + t_step, t_step))#copy.deepcopy(time_tot)
fonp_sim = [math.exp(a + b*t) for t in time_sim]
fonp_sim_up = [math.exp(a_int[1] + b_int[1]*t) for t in time_sim]
fonp_sim_dn = [math.exp(a_int[0] + b_int[0]*t) for t in time_sim]

#time_sim, fonp_sim = zip(*sorted(zip(time_sim, fonp_sim)))

ax.scatter(time_tot, fonp_tot, label='data')
ax.plot(time_sim, fonp_sim, 'r-', label='fit')
ax.plot(time_sim, fonp_sim_up, 'y-', label='fit up')
ax.plot(time_sim, fonp_sim_dn, 'y-', label='fit down')
ax.legend(loc='upper right')
ax.set(xlabel='Time (min)', ylabel='flow/pressure (mg/s bar)', title='')
ax.set_yscale('log')
pyplot.show()



fig, ax = pyplot.subplots() 
#print(time_tot)
#print(fonp_tot_log)

press_expt = []
for idx, pres in enumerate(press_tot):
	press_expt.append(pres*(math.exp(a + b*time_tot[idx])))


#time_sim, fonp_sim = zip(*sorted(zip(time_sim, fonp_sim)))

ax.scatter(press_expt, flow_tot, label='data')
ax.legend(loc='upper right')
ax.set(xlabel='Pressure*exp(a + b*Time) (mbar)', ylabel='flow (mg/s)', title='')
#ax.set_yscale('log')
pyplot.show()



	

		

