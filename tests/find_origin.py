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
	circles = cv2.HoughCircles(blur_gray, cv2.HOUGH_GRADIENT, 1.,100, param1=150,param2=30,minRadius=1,maxRadius=15)
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
			cv2.circle(line_image, (x, y), r,(0,0,100),2)
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
			if r < 80:
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
	
pic = 'C:\\Users\\LitePlacer\\Documents\\liteplacer-glue\\images\\webcam\\square_test_notimeout_it_1_home_2020_Jun_08.png'
print(get_circle(pic))
plot_circles(pic)
