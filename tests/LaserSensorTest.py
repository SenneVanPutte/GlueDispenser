import os
import cv2
import csv
import sys
import time
import random
import datetime
import winsound
import numpy as np
from time import sleep
from datetime import datetime
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')#C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')
from gcode_handler import gcode_handler
from LaserSensor import LaserSensor


def takePicture(name):
    status,img=vc.read()
    status,img=vc.read()
    cv2.imwrite(str(name)+'.jpg', img)
    cv2.waitKey(1)
def camera_init():
    initialization of digital camera
	vc=cv2.VideoCapture(1)
    if vc.isOpened():
        status,img=vc.read()
    else:
        print("err in openning")

if __name__ == '__main__':

    
    LaserSensor=LaserSensor('COM8') #constructing the laser sensor object
    machine = gcode_handler()
    

    machine.init_code()
    
    lx=LaserSensor.EdgeDetection(machine,[-7-LaserSensor.get_dx0(),62+35-LaserSensor.get_dy0()],10,'x','Laser',15+0.5,ToolsWidth=0.890)
    ly=LaserSensor.EdgeDetection(machine,[-5+20-LaserSensor.get_dx0(),60+25-LaserSensor.get_dy0()],5,'y','Laser',15+0.5,ToolsWidth=0.890)
    nx=LaserSensor.EdgeDetection(machine,[-7,60+35],10,'x','Needle',15+0.5,ToolsWidth=0.890)
    ny=LaserSensor.EdgeDetection(machine,[-5+20,60+25],10,'y','Needle',15+0.5,ToolsWidth=0.890)

    laserxy=[lx,ly]
    needlexy=[nx,ny]
    LaserSensor.SetXYOffset(laserxy,needlexy)
    
  
    #LaserSensor.set_dxy0(39.647,64.452)
    LaserSensor.ZCalibration(machine,-5,60,aprxHightOfObject=2.5)
    for i in range (10):
        print("###",i)
        LaserSensor.GotoXYZ(machine,x=-5+34,y=60+50+10,z=1)
    print("finished")
    
    winsound.Beep(2500, 2)
    exit()

