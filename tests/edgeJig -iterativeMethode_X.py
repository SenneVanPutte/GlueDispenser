#import matplotlib.pyplot as plt
#import pylab as plb
#import numpy as np
import winsound
import ctypes
import serial
import time
import math
import sys
#import cv2
import os
#from mpl_toolkits.mplot3d import Axes3D
#from scipy.optimize import curve_fit
#from numpy import asarray as ar,exp
from ctypes import windll, c_double
from datetime import datetime
from threading import Thread
from time import sleep
import numpy as np
#beep parameter
frequency = 2500  # Set Frequency To 2500 Hertz
duration = 1000  # Set Duration To 1000 ms == 1 second
ser = serial.Serial('COM8',115200)

	
n=0 

xComPort=3
yComPort=6
zComPort=7

xPS = 4
yPS = 6
zPS = 3
nAxis=1
nPosF=25000
#xDistance=5.0
#yDistance=2.0
#zDistance=5
#nExport=0
#z_value=-0.3

dll_name = "ps10.dll"
dllabspath = os.path.dirname(os.path.abspath(__file__)) + os.path.sep + dll_name
# load library
# give location of dll
#print(dllabspath)
mydll = windll.LoadLibrary(dllabspath)

def setup_stage(dll_ref,PS,ComPort,speed,absolute):
    stage=dll_ref.PS10_Connect(PS, 0, ComPort, 9600,0,0,0,0)
    stage=dll_ref.PS10_MotorInit(PS, 1)
    stage=dll_ref.PS10_SetTargetMode(PS, 1, absolute)
    if speed > 0:
        stage=dll_ref.PS10_SetPosF(PS, 1, speed)
    return dll_ref,stage
	
mydll,xstage = setup_stage(mydll,xPS,xComPort,nPosF,1)
mydll,ystage = setup_stage(mydll,yPS,yComPort,nPosF,1)
mydll,zstage = setup_stage(mydll,zPS,zComPort,nPosF,1)
print( "State x= ", (xstage))
print( "State y= ", (ystage))
print( "State z= ", (zstage))
GetPositionEx=mydll.PS10_GetPositionEx
GetPositionEx.restype = ctypes.c_double


##`````````````````````````````````````````````````

def moveX(xSteps):
    xReadOutStart=GetPositionEx(xPS, nAxis)
    xstage=mydll.PS10_MoveEx(xPS, nAxis, c_double(xSteps),1)
    xstate= mydll.PS10_GetMoveState(xPS, nAxis)
    while(xstate > 0):
        xstate = mydll.PS10_GetMoveState(xPS, nAxis)
        #camera(0)
    xReadOutEnd=GetPositionEx(xPS, nAxis)
    return xReadOutEnd
    #print( "X motor state = ", xstate ," from %3.3f" %(xReadOutStart) , " to %3.3f"%( xReadOutEnd))			
def moveY(ySteps):
    yReadOutStart=GetPositionEx(yPS, nAxis)
    ystage=mydll.PS10_MoveEx(yPS, nAxis, c_double(ySteps),1)
    ystate= mydll.PS10_GetMoveState(yPS, nAxis)
    while(ystate > 0):
        ystate = mydll.PS10_GetMoveState(yPS, nAxis)
        #camera(0)
    yReadOutEnd=GetPositionEx(yPS, nAxis)
    #print( "Y motor state = ", ystate ," from %3.3f" %(yReadOutStart) , " to %3.3f"%( yReadOutEnd))	
def moveZ(zSteps):
    zReadOutStart=GetPositionEx(zPS, nAxis)
    zstage=mydll.PS10_MoveEx(zPS, nAxis, c_double(zSteps),1)
    zstate= mydll.PS10_GetMoveState(zPS, nAxis)
    while(zstate > 0):
        zstate = mydll.PS10_GetMoveState(zPS, nAxis)
    zReadOutEnd=GetPositionEx(zPS, nAxis)
    time.sleep(0.001)
    return zReadOutStart #sharpness is calculated for start positin
    #print( "Z motor state = ", zstate ," from ", zReadOutStart , " to " , zReadOutEnd)
	
winsound.Beep(frequency, duration)

#
moveY(0)
#moveZ(0)
#edge=14.757 #12.25
#y=4.172
#margin=0.05
for v in range(5):
    file1 = open('result_'+str(v)+'.txt',"w")
    result = open('result.txt',"w")
    detected_edge=0
    lineZ=np.linspace(12.2,13,1,endpoint=False)
    for i in lineZ:
        moveZ(round(i,3))
        n=0
        
        #L = ["Number","\t","time","\t","X","\t","Y","\t","Z","\n"]
        #file1.writelines(L)
        upperEdge=10.5#edge+margin
        lowerEdge=2.5#edge-margin
        #NumOfPoints=int((upperEdge-lowerEdge)/0.001)
        #line1y=np.linspace(lowerEdge,upperEdge,NumOfPoints,endpoint=False)
        
        
        #moveX(lowerEdge)
        #ser.write(b's')
        #last_value=round((int(ser.readline().decode().strip())-7472.3525)/1264.9595,4)
        condition=True
        r=[0,0,0]
        k=0
        m=0
        pre_up_Edge,pre_down_Edge=0,0
        while condition:
            line_test=np.linspace(lowerEdge,upperEdge,3,endpoint=True)
            for j in line_test:
                moveX(round(j,3))
                sleep(0.3)
                ser.write(b's')
                r[k]=round((int(ser.readline().decode().strip())-7472.3525)/1264.9595,3)
                #r[k]=ser.readline().decode().strip()
                #print(r[k],k)
                k+=1
            k=0
            #print ("#############")
            #print (line_test)
            #print (r)
            
            #print("r[0]",r[0])
            #print("r[1]",r[1])
            #print("r[1]",r[2])
            #print("abs(r[0])-abs(r[1])",abs(r[0])-abs(r[1]))
            #print("abs(r[1])-abs(r[2])",abs(r[1])-abs(r[2]))
            
            if abs(abs(r[0])-abs(r[1]))>1.5:
                lowerEdge=round(line_test[0],3)
                upperEdge=round(line_test[1],3)
                pre_up_Edge=round(line_test[2],3)
                pre_down_Edge=round(line_test[0],3)
            elif abs(abs(r[1])-abs(r[2]))>1.5:
                lowerEdge=round(line_test[1],3)
                upperEdge=round(line_test[2],3)
                pre_up_Edge=round(line_test[2],3)
                pre_down_Edge=round(line_test[0],3)
            else:
                print("error",r,line_test)
                m+=1
                #lowerEdge=pre_down_Edge
                #upperEdge=pre_up_Edge
                if m>4:
                    condition=False
                    m=0
            #print(">>",lowerEdge,upperEdge,upperEdge-lowerEdge)
            if upperEdge-lowerEdge<0.003:
                #print("~~~~~~~~~~~~",lowerEdge)
                detected_edge=lowerEdge
                print("## i: ",i,detected_edge)
                now = datetime.now()
                L=[str(i),"\t",now.strftime("%H:%M:%S"),"\t",str('%5.3f' %(detected_edge)),"\n"]
                file1.writelines(L)
                condition=False
    file1.close()        
        #if abs(r[1]-r[2]>1):
        #    print("Hi")
        



"""

            
    edge=0
    for p in line1y:#partA_points_2D:
        moveX(round(p,3))
        sleep(0.1)
        ser.write(b's')
        z=round((int(ser.readline().decode().strip())-7472.3525)/1264.9595,4)
        x=GetPositionEx(xPS, nAxis)
        y=GetPositionEx(yPS, nAxis)
        now = datetime.now()
        print("#%d"%(n),now.strftime("%H:%M:%S")," x:%5.3f y:%5.3f "%(x,y),z)
        L=[str(n),"\t",now.strftime("%H:%M:%S"),"\t",str('%5.3f' %(x)),"\t",str('%5.3f' %(y)),"\t",str(z),"\n"]
        file1.writelines(L)
        n=n+1
        if abs(last_value-z)>1:
            print("edge detected...",x,GetPositionEx(zPS, nAxis))
            edge=x
        last_value=z
        
    L2=[str('%5.3f'%(GetPositionEx(zPS, nAxis))),"\t",str('%5.3f'%(edge)),"\n"]	
    result.writelines(L2)
"""    
result.close()
    




winsound.Beep(2000, duration)
winsound.Beep(2200, duration)
winsound.Beep(2500, duration)
closingx=mydll.PS10_Disconnect(xPS)
closingy=mydll.PS10_Disconnect(yPS)
closingz=mydll.PS10_Disconnect(zPS)
print("!!!!!!!!!!!!!!!FINISHED!!!!!!!!!!!!!!!")
