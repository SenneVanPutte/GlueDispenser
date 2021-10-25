import os
import cv2
import sys
import time
import math
import copy
import datetime
import numpy as np
import matplotlib.pyplot as plt
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')
from gcode_handler import gcode_handler

#480x640 camera dim

def pix_coo(x, y):
	x_res = 640
	y_res = 480
	
	x_c = x - x_res/2 
	y_c = y - y_res/2 
	
	return x_c, y_c
	
def radius(x, y):
	return math.sqrt(x*x + y*y)

def get_circles(image_file):
	img = cv2.imread(image_file)
	#print(img.shape)
	gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	kernel_size = 5
	blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)
	#circles = cv2.HoughCircles(blur_gray, cv2.HOUGH_GRADIENT, 0.1,100, param1=150,param2=90,minRadius=55,maxRadius=120)
	circles = cv2.HoughCircles(blur_gray, cv2.HOUGH_GRADIENT, 1.,100, param1=150,param2=90,minRadius=55,maxRadius=120)
	return circles

def plot_circles(image_file, file_name=None):
	img = cv2.imread(image_file)
	#print(image_file)
	#cv2.imshow('image', img)
	cv2.waitKey(0)
	line_image = np.copy(img) * 0
	circles = get_circles(image_file)
	for circle in circles:
		for x, y, r in circle:
			#print('Radius: '+str(r)+', x: '+str(x)+', y: '+str(y))
			cv2.circle(line_image, (x, y), r,(255,0,0),5)
	lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)
	cv2.imshow('image', lines_edges)
	if not file_name is None:
		cv2.imwrite(file_name, lines_edges)
	cv2.waitKey(0)
	
def get_circle(image_file):
	
	xx = 0
	yy = 0
	rr = 0
	circles = get_circles(image_file)
	for circle in circles:
		for x, y, r in circle:
			if r > 80:
				rr = r
				yy = y
				xx = x 
	return rr, xx, yy

def median(listy):
	tmp = copy.deepcopy(listy)
	tmp.sort()
	if len(tmp)%2:
	    return tmp[len(tmp)/2]
	else:
		return (tmp[len(tmp)/2] + tmp[len(tmp)/2 - 1] + 0.)/2.
	
ii = []	
TL_x = []
TL_y = []
TL_r = []
TR_x = []
TR_y = []
TR_r = []
BL_x = []
BL_y = []
BL_r = []
BR_x = []
BR_y = []
BR_r = []

r_c = []
r_p = []

title = ''
for i_pic in range(10):
	print('Searching picture '+str(i_pic))
	
	#title = 'nohoming_timeout'
	#TL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_'+str(i_pic)+'_before_x_40_y_115_2020_Jun_08.png'
	#TR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_'+str(i_pic)+'_before_x_140_y_115_2020_Jun_08.png'
	#BL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_'+str(i_pic)+'_before_x_40_y_15_2020_Jun_08.png'
	#BR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_'+str(i_pic)+'_before_x_140_y_15_2020_Jun_08.png'
	
	#title = 'homing_timeout'
	#TL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_it_'+str(i_pic)+'_before_x_40_y_115_2020_Jun_08.png'
	#TR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_it_'+str(i_pic)+'_before_x_140_y_115_2020_Jun_08.png'
	#BL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_it_'+str(i_pic)+'_before_x_40_y_15_2020_Jun_08.png'
	#BR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_it_'+str(i_pic)+'_before_x_140_y_15_2020_Jun_08.png'
	
	#title = 'nohoming_notimeout'
	#TL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_nohoming_it_'+str(i_pic)+'_x_40_y_115_2020_Jun_08.png'
	#TR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_nohoming_it_'+str(i_pic)+'_x_140_y_115_2020_Jun_08.png'
	#BL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_nohoming_it_'+str(i_pic)+'_x_40_y_15_2020_Jun_08.png'
	#BR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_nohoming_it_'+str(i_pic)+'_x_140_y_15_2020_Jun_08.png'

	title = 'homing_notimeout'
	TL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_it_'+str(i_pic)+'_x_40_y_115_2020_Jun_08.png'
	TR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_it_'+str(i_pic)+'_x_140_y_115_2020_Jun_08.png'
	BL_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_it_'+str(i_pic)+'_x_40_y_15_2020_Jun_08.png'
	BR_image= 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_it_'+str(i_pic)+'_x_140_y_15_2020_Jun_08.png'

	#plot_circles(TL_image, 'C:\\Users\\LitePlacer\\Desktop\\senne\\TL_nohoming_timeout_'+str(i_pic)+'.png')
	#plot_circles(TR_image)
	#plot_circles(BR_image)
	
	tl_r, tl_x, tl_y = get_circle(TL_image)
	tr_r, tr_x, tr_y = get_circle(TR_image)
	bl_r, bl_x, bl_y = get_circle(BL_image)
	br_r, br_x, br_y = get_circle(BR_image)
	
	tl_x_pix, tl_y_pix = pix_coo(tl_x, tl_y)
	#print(tl_x, tl_y, tl_x_pix, tl_y_pix, radius(tl_x_pix, tl_y_pix))
	r_p.append(radius(tl_x_pix, tl_y_pix))
	tr_x_pix, tr_y_pix = pix_coo(tr_x, tr_y)
	r_p.append(radius(tr_x_pix, tr_y_pix))
	bl_x_pix, bl_y_pix = pix_coo(bl_x, bl_y)
	r_p.append(radius(bl_x_pix, bl_y_pix))
	br_x_pix, br_y_pix = pix_coo(br_x, br_y)
	r_p.append(radius(br_x_pix, br_y_pix))
	
	r_c.append(tl_r)
	r_c.append(tr_r)
	r_c.append(bl_r)
	r_c.append(br_r)

	TL_x.append(tl_x)
	TL_y.append(tl_y)
	TL_r.append(tl_r)
	TR_x.append(tr_x)
	TR_y.append(tr_y)
	TR_r.append(tr_r)
	BL_x.append(bl_x)
	BL_y.append(bl_y)
	BL_r.append(bl_r)
	BR_x.append(br_x)
	BR_y.append(br_y)
	BR_r.append(br_r)
	
	ii.append(i_pic)

place = 'C:\\Users\\LitePlacer\\Desktop\\senne\\'

LS = [radius(TL_x[idx] - BL_x[idx], (TL_y[idx]+1000) - BL_y[idx]) - 1000 for idx in range(len(TL_x))]
RS = [radius(TR_x[idx] - BR_x[idx], (TR_y[idx]+1000) - BR_y[idx]) - 1000 for idx in range(len(TR_x))]

TS = [radius((TR_x[idx]+1000) - TL_x[idx], TR_y[idx] - TL_y[idx]) - 1000 for idx in range(len(TR_x))]
BS = [radius((BR_x[idx]+1000) - BL_x[idx], BR_y[idx] - BL_y[idx]) - 1000 for idx in range(len(TR_x))]


R = TL_r + TR_r + BL_r + BR_r
R.sort()
medianR = median(R)
scale = 10000./(medianR+0.)
scale_d = 10000./(R[0]+0.)
scale_u = 10000./(R[-1]+0.)
print(scale, scale_d, scale_u)

scale_mm = scale/1000.

#LS_m = (sum(LS) + 0.)/(len(LS) + 0.)
#RS_m = (sum(RS) + 0.)/(len(RS) + 0.)
#TS_m = (sum(TS) + 0.)/(len(TS) + 0.)
#BS_m = (sum(BS) + 0.)/(len(BS) + 0.)

LS_m = median(LS)
RS_m = median(RS)
TS_m = median(TS)
BS_m = median(BS)

LS_r = [(val - LS_m)*scale_mm for val in LS]
RS_r = [(val - RS_m)*scale_mm for val in RS]
TS_r = [(val - TS_m)*scale_mm for val in TS]
BS_r = [(val - BS_m)*scale_mm for val in BS]
	
#TL_xb = (sum(TL_x) + 0.)/(len(TL_x)+0.)
#TR_xb = (sum(TR_x) + 0.)/(len(TL_x)+0.)
#BL_xb = (sum(BL_x) + 0.)/(len(TL_x)+0.)
#BR_xb = (sum(BR_x) + 0.)/(len(TL_x)+0.)

#TL_yb = (sum(TL_y) + 0.)/(len(TL_x)+0.)
#TR_yb = (sum(TR_y) + 0.)/(len(TL_x)+0.)
#BL_yb = (sum(BL_y) + 0.)/(len(TL_x)+0.)
#BR_yb = (sum(BR_y) + 0.)/(len(TL_x)+0.)

TL_xb = median(TL_x)
TR_xb = median(TR_x)
BL_xb = median(BL_x)
BR_xb = median(BR_x)

TL_yb = median(TL_y)
TR_yb = median(TR_y)
BL_yb = median(BL_y)
BR_yb = median(BR_y)

TL_xr = [(x-TL_xb)*scale_mm for x in TL_x]
TR_xr = [(x-TR_xb)*scale_mm for x in TR_x]
BL_xr = [(x-BL_xb)*scale_mm for x in BL_x]
BR_xr = [(x-BR_xb)*scale_mm for x in BR_x]

TL_yr = [(y-TL_yb)*scale_mm for y in TL_y]
TR_yr = [(y-TR_yb)*scale_mm for y in TR_y]
BL_yr = [(y-BL_yb)*scale_mm for y in BL_y]
BR_yr = [(y-BR_yb)*scale_mm for y in BR_y]

fig, ax = plt.subplots()
ax.plot(ii, LS_r, label='LS')
ax.plot(ii, RS_r, label='RS')
ax.plot(ii, TS_r, label='TS')
ax.plot(ii, BS_r, label='BS')
ax.set(xlabel='Iteration', ylabel='$\Delta$L [mm]')
ax.legend()
ax.set_ylim([-0.5,2.1])
plt.savefig(place+title+'_l.png')
plt.show()

#fig, ax = plt.subplots()
#ax.plot(ii, TL_x, label='TL')
#ax.plot(ii, TR_x, label='TR')
#ax.plot(ii, BL_x, label='BL')
#ax.plot(ii, BR_x, label='BR')

#ax.plot(ii, TL_y, label='TL')
#ax.plot(ii, TR_y, label='TR')
#ax.plot(ii, BL_y, label='BL')
#ax.plot(ii, BR_y, label='BR')

fig, ax = plt.subplots()
ax.plot(ii, TL_xr, label='TL')
ax.plot(ii, TR_xr, label='TR')
ax.plot(ii, BL_xr, label='BL')
ax.plot(ii, BR_xr, label='BR')
ax.set(xlabel='Iteration', ylabel='$\Delta$x [mm]')
ax.legend()
ax.set_ylim([-0.3,0.6])
plt.savefig(place+title+'_x.png')
plt.show()

fig, ax = plt.subplots()
ax.plot(ii, TL_yr, label='TL')
ax.plot(ii, TR_yr, label='TR')
ax.plot(ii, BL_yr, label='BL')
ax.plot(ii, BR_yr, label='BR')
ax.set(xlabel='Iteration', ylabel='$\Delta$y [mm]')
ax.legend()
ax.set_ylim([-2.,2.])
plt.savefig(place+title+'_y.png')
plt.show()

#ax.plot(ii, TL_r, label='TL')
#ax.plot(ii, TR_r, label='TR')
#ax.plot(ii, BL_r, label='BL')
#ax.plot(ii, BR_r, label='BR')

#ax.plot(TL_x, TL_y, label='TL')
#ax.plot(TR_x, TR_y, label='TR')
#ax.plot(BL_x, BL_y, label='BL')
#ax.plot(BR_x, BR_y, label='BR')

fig, ax = plt.subplots()
ax.plot(TL_xr, TL_yr, label='TL')
ax.plot(TR_xr, TR_yr, label='TR')
ax.plot(BL_xr, BL_yr, label='BL')
ax.plot(BR_xr, BR_yr, label='BR')
ax.set(xlabel='$\Delta$x [mm]', ylabel='$\Delta$y [mm]')
ax.legend()
ax.set_ylim([-2.,2.])
ax.set_xlim([-2.,2.])
ax.set_aspect('equal', adjustable='box')
plt.savefig(place+title+'_xy.png')
plt.show()

#ax.scatter(r_p, r_c)

#ax.legend()
#plt.show()
#raw_input('end')
	
#image = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_9_before_x_140_y_115_2020_Jun_08.png'
#image = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_9_before_x_140_y_15_2020_Jun_08.png'
#image = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_9_before_x_40_y_115_2020_Jun_08.png'
#image = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_timeout_nohoming_it_9_before_x_40_y_15_2020_Jun_08.png'
#img = cv2.imread(image)
#gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#kernel_size = 5
#blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

#low_threshold = 150
#high_threshold = 250
#edges = cv2.Canny(blur_gray, low_threshold, high_threshold)


#rho = 1  # distance resolution in pixels of the Hough grid
#theta = np.pi / 180  # angular resolution in radians of the Hough grid
#threshold = 15  # minimum number of votes (intersections in Hough grid cell)
#min_line_length = 50  # minimum number of pixels making up a line
#max_line_gap = 20  # maximum gap in pixels between connectable line segments
#line_image = np.copy(img) * 0  # creating a blank to draw lines on

# Run Hough on edge detected image
# Output "lines" is an array containing endpoints of detected line segments
#lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
#                    min_line_length, max_line_gap)
					
#circles = cv2.HoughCircles(blur_gray, cv2.HOUGH_GRADIENT, 0.1,100, param1=150,param2=90,minRadius=20,maxRadius=110)

#for circle in circles:
#	for x, y, r in circle:
#		print('Radius: '+str(r)+', x: '+str(x)+', y: '+str(y))
#		cv2.circle(line_image, (x, y), r,(255,0,0),5)
	
#lines_edges = cv2.addWeighted(img, 0.8, line_image, 1, 0)

#cv2.imshow('image', lines_edges)
#cv2.waitKey(0)
