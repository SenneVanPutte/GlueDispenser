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

LOG_DIR = '.'
month_dict = dict((k,v) for v,k in enumerate(calendar.month_abbr))

up_date = '2019_Dec_11'
dn_date = '2019_Oct_23'

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
# inp_Time_splt = inp_Time.split(':')
# now = datetime.datetime.now()
# year = int(inp_Time_splt[0])
# month = int(inp_Time_splt[1])
# day = int(inp_Time_splt[2])
# hour = int(inp_Time_splt[3])
# min = int(inp_Time_splt[4])
# #ts = calendar.timegm(datetime.datetime(year, month, day, hour, min).timetuple())
# ts = time.mktime(datetime.datetime(year, month, day, hour, min).timetuple())
# print(ts)
# print(time.time())



Time_lst = []
flow_lst = []
pres_lst = []
fonp_lst = []

Time_dict = {}
flow_dict = {}
pres_dict = {}
fonp_dict = {}
glts_dict = {}
for log in log_lst:
	log_file = open(log, 'r')
	lines = log_file.readlines()
	log_file.close()
	
	Time_dict[log] = []
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
		
		Time_lst.append(Time)
		pres_lst.append(pres)
		flow_lst.append(flow)
		fonp_lst.append(flow/(pres + 0.))
		
		Time_dict[log].append(Time)
		pres_dict[log].append(pres)
		flow_dict[log].append(flow)
		fonp_dict[log].append(flow/(pres/1000. + 0.))
		
		
 
		
fig, ax = pyplot.subplots() 
#ax.scatter(Time_lst, flow_lst, label='measurement')
#ax.scatter(pres_lst, flow_lst, label='measurement')
ax.scatter(Time_lst, fonp_lst, label='measurement')
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

for log in Time_dict:
	Time = Time_dict[log]
	fonp = fonp_dict[log]
	press = pres_dict[log]
	flow = flow_dict[log]
	
	Time_rel = []
	ts = glts_dict[log]
	for t in Time:
		rel_timy = []
		for tsy in ts:
			t_diff = t - tsy
			if t_diff < 0.: continue
			else: rel_timy.append(t_diff)
		if len(rel_timy) == 0: Time_rel.append(t - Time[0])
		elif len(rel_timy) == 1: Time_rel.append(rel_timy[0])
		else: Time_rel.append(min(rel_timy))
	
	time_rel_rs = [t/60. for t in Time_rel]
	fonp_log = [math.log(r) for r in fonp]
	
	#Time_rel = [(t - Time[0])/60. for t in Time]
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



	

		

