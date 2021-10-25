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

SCALE_POSITION = [350, 200]
def TouchSurf(x,y,aprxHightOfObject=2,speed=5):
    machine.down(10)
    machine.gotoxy(x,y)
    machine.down(42-aprxHightOfObject)
    #time.sleep(5)
    x_,y_,z_=machine.probe_z(speed=5, up_rel=0.1)
    machine.down(z_-10) #needle go to safe height
    return x_,y_,z_  

def LaserSensorGotoXYZ(machine,x,y,z=None):
    machine.gotoxy(x-LaserSensor.get_dx0(),y-LaserSensor.get_dy0())#Laser
    if z!=None:
        machine.down(float(z))		#go to that height    
        print("same height",z)
    corrected_y=LaserSensor.dy(LaserSensor.Height())
    machine.gotoxy(x-LaserSensor.get_dx0(),y-LaserSensor.get_dy0()+corrected_y) #corrected point
    return LaserSensor.Height()
def calibration(x,y,aprxHightOfObject=24):
    x_,y_,z_=TouchSurf(float(x),float(y),aprxHightOfObject,speed=20)   #needle go to x,y and touch the surface to measure height by touch sensor =>z_
    machine.gotoxy(x-LaserSensor.get_dx0(),y-LaserSensor.get_dy0())#Laser 
    machine.down(z_)											   #Laser go to same height as surface was
    different_height_for_calibration=5                             #offset of height to do calibration (for valid data)
    machine.down(z_-different_height_for_calibration)	           #move machine to height
    machine.gotoxy(x-LaserSensor.get_dx0()+LaserSensor.dx(different_height_for_calibration),y-LaserSensor.get_dy0()+LaserSensor.dy(different_height_for_calibration)) #correct x,y base on height
    LaserSensor.Calibration(default_height=different_height_for_calibration,bent=0.0)              #Laser calibration
    LZ=np.linspace(z_-5,z_-14,3,endpoint=True)#Sensor:37+55
    name="calibration result by machine.txt"
    L=["Z","\t","Time","\t","Height by machine(z_-lz)","\t","Laser","\t","difference","\n"]				
    with open(name, "a") as myfile:myfile.writelines(L)
    print("SM","\t","Sensor","\t","Diff")
    loadcell=[]
    laser=[]
    for lz in LZ:
        machine.down(lz)
        machine.gotoxy(x-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height()),y-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height()))
        L=[str(lz),"\t",datetime.now().strftime("%H:%M:%S"),"\t",str(round(z_-lz,3)),"\t",str(LaserSensor.Height()),"\t",str(round(z_-lz-LaserSensor.Height(),3)),"\n"]				
        with open(name, "a") as myfile:myfile.writelines(L)
        hh=LaserSensor.Height()
        loadcell.append(round(z_-lz,3))
        laser.append(LaserSensor.Height())
        print(round(z_-lz,3),"\t",hh,"\t",round(z_-lz-hh,3),LaserSensor.Valid())
    m,b=np.polyfit(loadcell,laser,1)
    print(m,b)
    L=["m:","\t",str(round(m,3)),"\t","b","\t",str(round(b,3)),"\n"]				
    with open(name, "a") as myfile:myfile.writelines(L)
    if abs(b)>=0.025:
        machine.down(z_-5)
        LaserSensor.Calibration(default_height=5,bent=0.0+b)
        print("SM","\t","Sensor","\t","Diff")
        loadcell_=[]
        laser_=[]
        for lz in LZ:
            machine.down(lz)
            machine.gotoxy(x-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height()),y-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height()))
            L=[str(lz),"\t",datetime.now().strftime("%H:%M:%S"),"\t",str(round(z_-lz,3)),"\t",str(LaserSensor.Height()),"\t",str(round(z_-lz-LaserSensor.Height(),3)),"\n"]				
            with open(name, "a") as myfile:myfile.writelines(L)
            hh=LaserSensor.Height()
            loadcell_.append(round(z_-lz,3))
            laser_.append(hh)
            print(round(z_-lz,3),"\t",hh,"\t",round(z_-lz-hh,3))
        m,b=np.polyfit(loadcell_,laser_,1)
        print(m,b)
        L=["m:","\t",str(round(m,3)),"\t","b","\t",str(round(b,3)),"\n"]				
        with open(name, "a") as myfile:myfile.writelines(L)
        L=["##------------------------------------------------##\n"]				
        with open(name, "a") as myfile:myfile.writelines(L)
    machine.down(10)
    print("Z calibration had been finished!!!")
def takePicture(name):
    status,img=vc.read()
    status,img=vc.read()
    cv2.imwrite(str(name)+'.jpg', img)
    cv2.waitKey(1)
def EdgeDetection(StartPoint_xy,ScanningRange,Direction,NeedleOrLaser,aprxHightOfObject,ToolsWidth=0):
    #if Direction!='x' or Direction!='y':
    #    print("Error in Direction value!!!")
    #    return None
    #if NeedleOrLaser!='Laser' or NeedleOrLaser!='Needle':
    #    print("Error in NeedleOrLaser value!!!")
    #    return None
    #print(StartPoint_xy)
    upperEdge=StartPoint_xy[0] if Direction=='x' else StartPoint_xy[1] 
    lowerEdge=upperEdge-ScanningRange
    #print("Up Down",upperEdge,lowerEdge)
    UE=upperEdge
    LE=lowerEdge
    condition=True
    r=[0,0,0]
    attempt=0
    threshould_edge=0.7
    detected_edge=0
    while condition:
        line_test=np.linspace(lowerEdge,upperEdge,3,endpoint=True)
        print("line:::",line_test)
        for k,j in enumerate( line_test):
            
            if NeedleOrLaser=='Needle':
                if Direction=='x':
                    machine.gotoxy(round(j,3),StartPoint_xy[1])
                if Direction=='y':
                    machine.gotoxy(StartPoint_xy[0],round(j,3))
                machine.down(42-aprxHightOfObject)
                r[k]=machine.probe_z(speed=20, up_rel=0.5)[2]
                machine.down(42-aprxHightOfObject)
            if NeedleOrLaser=='Laser':
                if Direction=='x':
                    machine.gotoxy(round(j,3)-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height()),StartPoint_xy[1]-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height()))
                if Direction=='y':
                    machine.gotoxy(StartPoint_xy[0]-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height()),round(j,3)-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height()))
                machine.down(24)
                r[k]=LaserSensor.Height()
        if abs(r[0]-r[1])>threshould_edge:
            lowerEdge=round(line_test[0],3)#-0.01
            upperEdge=round(line_test[1],3)#+0.01
        elif abs(r[1]-r[2])>threshould_edge:
            lowerEdge=round(line_test[1],3)#-0.01
            upperEdge=round(line_test[2],3)#+0.01
        else:
            lowerEdge=LE
            upperEdge=UE+1
            #print("Err",attempt,r,line_test)
            attempt+=1
            if attempt>5:
                condition=False
                attempt=0
                print("Error in finding edge")
        if upperEdge -lowerEdge <0.7:
            fine_line=np.linspace(upperEdge+0.05,lowerEdge-0.05,16,endpoint=True)
            h_0=machine.probe_z(speed=20, up_rel=0.5)[2] if NeedleOrLaser=='Needle' else LaserSensor.Height()
            for fine_step in fine_line:
                if NeedleOrLaser=='Laser':
                    if Direction=='x':
                        machine.gotoxy(round(fine_step,3)-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height()),StartPoint_xy[1]-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height()))
                    if Direction=='y':
                        machine.gotoxy(StartPoint_xy[0]-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height()),round(fine_step,3)-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height()))
                if NeedleOrLaser=='Needle':
                    if Direction=='x':
                        machine.gotoxy(round(fine_step,3),StartPoint_xy[1])
                    if Direction=='y':
                        machine.gotoxy(StartPoint_xy[0],round(fine_step,3))
                
                new_value=machine.probe_z(speed=20, up_rel=0.5)[2] if NeedleOrLaser=='Needle' else LaserSensor.Height()
                
                if abs(new_value-h_0)>threshould_edge:
                    detected_edge=round(fine_step,3)
                    print("Detected edge: ",detected_edge)
                    condition=False
                    machine.down(10)
                    #if NeedleOrLaser=='Laser':
                    #    if Direction=='x': Laser.
                    if NeedleOrLaser=='Laser':
                        if Direction=='x':
                            detected_edge=detected_edge-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height())
                        if Direction=='y':
                            detected_edge=detected_edge-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height())
                    if NeedleOrLaser=='Needle':
                        detected_edge=detected_edge+ToolsWidth/2.0 
                    return detected_edge
                    break

"""    
def NeedlePosition_X(x,y,aprxHightOfObject,NeedleWidth):
    upperEdge=x
    lowerEdge=upperEdge-15
    UE=upperEdge
    LE=lowerEdge
    condition=True
    r=[0,0,0]
    k=0
    m=0
    threshould_edge=0.7
    detected_edge=0
    while condition:
        line_test=np.linspace(lowerEdge,upperEdge,3,endpoint=True)
        for j in line_test:
            machine.gotoxy((round(j,3)),y)
            machine.down(42-aprxHightOfObject)
            x_,y_,z_=machine.probe_z(speed=20, up_rel=0.2)
            r[k]=z_
            k+=1
            machine.down(42-aprxHightOfObject)
        k=0
        if abs(r[0]-r[1])>threshould_edge:
            lowerEdge=round(line_test[0],3)#-0.01
            upperEdge=round(line_test[1],3)#+0.01
            
        elif abs(r[1]-r[2])>threshould_edge:
            lowerEdge=round(line_test[1],3)#-0.01
            upperEdge=round(line_test[2],3)#+0.01
            
        else:
            lowerEdge=LE
            upperEdge=UE+1
            
            print("Err",m,r,line_test)
            m+=1

            if m>5:
                condition=False
                m=0
                print("Error in finding edge")
        if upperEdge -lowerEdge <0.7:
            fine_line=np.linspace(upperEdge+0.05,lowerEdge-0.05,16,endpoint=True)
            x_,y_,z_=machine.probe_z(speed=20, up_rel=0.5)
            h_0=z_
            for fine_step in fine_line:
                machine.gotoxy(round(fine_step,3),y)
                #print("moved to ",round(fine_step,3),LaserSensor.Height())	
                x_,y_,z_=machine.probe_z(speed=20, up_rel=0.5)
                
                if abs(z_-h_0)>threshould_edge:
                    detected_edge=round(fine_step,3)
                    print("detecteeeed >>>>",detected_edge)
                    condition=False
                    machine.down(10)
                    return detected_edge+NeedleWidth/2.0
                    break

def NeedlePosition_Y(x,y,aprxHightOfObject,NeedleWidth):
    upperEdge=y
    lowerEdge=upperEdge-5
    UE=upperEdge
    LE=lowerEdge
    condition=True
    r=[0,0,0]
    k=0
    m=0
    threshould_edge=0.7
    detected_edge=0
    while condition:
        line_test=np.linspace(lowerEdge,upperEdge,3,endpoint=True)
        for j in line_test:
            machine.gotoxy(x,(round(j,3)))
            machine.down(42-aprxHightOfObject)
            x_,y_,z_=machine.probe_z(speed=20, up_rel=0.2)
            r[k]=z_
            k+=1
            machine.down(42-aprxHightOfObject)
        k=0
        if abs(r[0]-r[1])>threshould_edge:
            lowerEdge=round(line_test[0],3)#-0.01
            upperEdge=round(line_test[1],3)#+0.01
            
        elif abs(r[1]-r[2])>threshould_edge:
            lowerEdge=round(line_test[1],3)#-0.01
            upperEdge=round(line_test[2],3)#+0.01
            
        else:
            lowerEdge=LE
            upperEdge=UE+1
            
            print("Err",m,r,line_test)
            m+=1

            if m>5:
                condition=False
                m=0
                print("Error in finding edge")
        if upperEdge -lowerEdge <0.7:
            fine_line=np.linspace(upperEdge+0.05,lowerEdge-0.05,16,endpoint=True)
            x_,y_,z_=machine.probe_z(speed=20, up_rel=0.5)
            h_0=z_
            for fine_step in fine_line:
                machine.gotoxy(x,round(fine_step,3))
                #print("moved to ",round(fine_step,3),LaserSensor.Height())	
                x_,y_,z_=machine.probe_z(speed=20, up_rel=0.5)
                
                if abs(z_-h_0)>threshould_edge:
                    detected_edge=round(fine_step,3)
                    print("detecteeeed >>>>",detected_edge)
                    condition=False
                    machine.down(10)
                    return detected_edge+NeedleWidth/2.0
                    break
def LaserPosition_X(x,y):
    upperEdge=x
    lowerEdge=upperEdge-10
    UE=upperEdge
    LE=lowerEdge
    condition=True
    r=[0,0,0]
    k=0
    m=0
    threshould_edge=0.7
    detected_edge=0
    while condition:
        line_test=np.linspace(lowerEdge,upperEdge,3,endpoint=True)
        for j in line_test:
            machine.gotoxy((round(j,3)),y)
            sleep(0.1)
            
            r[k]=LaserSensor.Height()
            k+=1
        k=0
        if abs(r[0]-r[1])>threshould_edge:
            lowerEdge=round(line_test[0],3)#-0.01
            upperEdge=round(line_test[1],3)#+0.01
        elif abs(r[1]-r[2])>threshould_edge:
            lowerEdge=round(line_test[1],3)#-0.01
            upperEdge=round(line_test[2],3)#+0.01
        else:
            lowerEdge=LE
            upperEdge=UE+1
            print("Err",m,r,line_test)
            m+=1
            if m>5:
                condition=False
                m=0
                print("Error in finding edge")
        if upperEdge -lowerEdge <0.7:
            fine_line=np.linspace(upperEdge+0.05,lowerEdge-0.05,16,endpoint=True)
            h_0=LaserSensor.Height()
            for fine_step in fine_line:
                machine.gotoxy(round(fine_step,3),y)					
                if abs(LaserSensor.Height()-h_0)>threshould_edge:
                    detected_edge=round(fine_step,3)
                    print("detecteeeed >>>>",detected_edge)
                    condition=False
                    machine.down(10)
                    return detected_edge
                    break
def LaserPosition_Y(x,y):
    upperEdge=y
    lowerEdge=upperEdge-15
    UE=upperEdge
    LE=lowerEdge
    condition=True
    r=[0,0,0]
    k=0
    m=0
    threshould_edge=0.7
    detected_edge=0
    while condition:
        line_test=np.linspace(lowerEdge,upperEdge,3,endpoint=True)
        for j in line_test:
            machine.gotoxy(x,(round(j,3)))
            sleep(0.1)
            
            r[k]=LaserSensor.Height()
            k+=1
        k=0
        if abs(r[0]-r[1])>threshould_edge:
            lowerEdge=round(line_test[0],3)#-0.01
            upperEdge=round(line_test[1],3)#+0.01
        elif abs(r[1]-r[2])>threshould_edge:
            lowerEdge=round(line_test[1],3)#-0.01
            upperEdge=round(line_test[2],3)#+0.01
        else:
            lowerEdge=LE
            upperEdge=UE+1
            print("Err",m,r,line_test)
            m+=1
            if m>5:
                condition=False
                m=0
                print("Error in finding edge")
        if upperEdge -lowerEdge <0.7:
            fine_line=np.linspace(upperEdge+0.05,lowerEdge-0.05,16,endpoint=True)
            h_0=LaserSensor.Height()
            for fine_step in fine_line:
                machine.gotoxy(x,round(fine_step,3))					
                if abs(LaserSensor.Height()-h_0)>threshould_edge:
                    detected_edge=round(fine_step,3)
                    print("detecteeeed >>>>",detected_edge)
                    condition=False
                    machine.down(10)
                    return detected_edge
                    break
"""
if __name__ == '__main__':
    vc=cv2.VideoCapture(1)
    if vc.isOpened():
        status,img=vc.read()
    else:
        print("err in openning")
    
    LaserSensor=LaserSensor('COM8') #constructing the laser sensor object
    machine = gcode_handler()
    print("before init",datetime.now().strftime("%H:%M:%S"))

    machine.init_code()
    L=["number","\t","time","\t","x","\t","y","\t","z","\t","surf by touch","\t","surf by laser","\t","machine loc","\n"]				
    fileName='repeat on a 1 point after each calibration.txt'
    with open(fileName, "a") as myfile:myfile.writelines(L)
    for i in range(100):
       LaserSensor.ZCalibration(machine,-5,60,aprxHightOfObject=2.5)
       print("#",i)
       h=LaserSensor.GotoXYZ(machine,127.1,222.6,.2)
       machineZLocation=h-.2
       time.sleep(0.5)
       takePicture(i)	 
       x_,y_,z_=machine.probe_z(speed=5, up_rel=0.2)
       machine.down(10)
       L=[str(i),"\t",datetime.now().strftime("%H:%M:%S"),"\t",str(127.1-39.97),"\t",str(222.6-64.45),"\t",str(222.5),"\t",str(z_),"\t",str(h),"\t",str(machineZLocation),"\n"]				
       with open(fileName, "a") as myfile:myfile.writelines(L)
    
    exit()
    print("after init",datetime.now().strftime("%H:%M:%S"))
    print("before laser x",datetime.now().strftime("%H:%M:%S"))
    lx=EdgeDetection([-7,62],10,'x','Laser',2.5,ToolsWidth=0.890)
    print("after laser x before laser y",datetime.now().strftime("%H:%M:%S"))
    ly=EdgeDetection([-5,60],10,'y','Laser',2.5,ToolsWidth=0.890)
    print("after laser y before needle x",datetime.now().strftime("%H:%M:%S"))
    nx=EdgeDetection([-5,60],10,'x','Needle',2.5,ToolsWidth=0.890)
    print("after needle x before needle y",datetime.now().strftime("%H:%M:%S"))
    ny=EdgeDetection([-5,60],10,'y','Needle',2.5,ToolsWidth=0.890)
    print("after needle y before calibration",datetime.now().strftime("%H:%M:%S"))
    laserxy=[lx,ly]
    needlexy=[nx,ny]
    print("laser",laserxy)
    print("needle",needlexy)
    print("dx0 , dy0",LaserSensor.get_dx0(),LaserSensor.get_dy0())
    LaserSensor.SetXYOffset(laserxy,needlexy)
    print("dx0 , dy0_new",LaserSensor.get_dx0(),LaserSensor.get_dy0())
    print("before z calibration",datetime.now().strftime("%H:%M:%S"))
    LaserSensor.ZCalibration(machine,-5,60,aprxHightOfObject=2.5)
    print("after Z calibration",datetime.now().strftime("%H:%M:%S"))
    #eyl=EdgeDetection([-5,60],'x','Laser',2.5,ToolsWidth=0.890)
    #print(eyl)
    #calibration(x=0,y=65,aprxHightOfObject=2.5)#65
    print("finished")
    exit()
    #now = datetime.now()
    #print("start",now.strftime("%H:%M:%S"))
    #print(NeedlePosition_X(x=0,y=65,aprxHightOfObject=2.5,NeedleWidth=0.89))
    #now = datetime.now()
    #print("stop",now.strftime("%H:%M:%S"))
    #exit()
	
    """	
    L=["number","\t","time","\t","x","\t","y","\t","set z","\t","touch","\t","laser","\t","machineZLocation+0.2","\n"]
    fileName="test.txt"
    with open(fileName, "a") as myfile:myfile.writelines(L)
    LX=np.linspace(37,37+75-6,10,endpoint=True)#Sensor:37+55
    LY=np.linspace(115,115+70+6,10,endpoint=True)#sensor:110+70 
    n=0
    for i in LX:
        for j in LY:
            n=n+1
            print(n)
            h=LaserSensor.GotoXYZ(machine,i,j,.2)
            			
            x_,y_,z_=machine.probe_z(speed=5, up_rel=0.2)
            machine.down(10) 
            now = datetime.now()				
            L=[str(i),"\t",now.strftime("%H:%M:%S"),"\t",str(127.1-39.97),"\t",str(222.6-64.45),"\t",str(222.5),"\t",str(z_),"\t",str(h),"\t",str(h),"\n"]				
            with open(fileName, "a") as myfile:myfile.writelines(L)  	
    exit()
    for i in range(100):
       print(i)
       h=LaserSensor.GotoXYZ(machine,127.1,222.6,.5)
	   machineZLocation=h-.5
       #machine.gotoxy(127.1,222.6)
       #machine.down(22.555)
       time.sleep(1)
       takePicture(i)	 
       x_,y_,z_=machine.probe_z(speed=5, up_rel=0.2)
       machine.down(10)
       #machine.gotoxy(127.1-39.97,222.6-64.45)
       time.sleep(0.5) 
       #now = datetime.now()				
       L=[str(i),"\t",datetime.now().strftime("%H:%M:%S"),"\t",str(127.1-39.97),"\t",str(222.6-64.45),"\t",str(222.5),"\t",str(z_),"\t",str(h),"\t",str(machineZLocation),"\n"]				
       with open(fileName, "a") as myfile:myfile.writelines(L)
    
    exit()
    
    #repeat height measurement above x, y with camera>>>
  
    L=["number","\t","time","\t","x","\t","y","\t","desireValue","\t","measured by touch","\t","measured by laser","\t","machine_pos","\t","gap","\n"]				
    with open("gapMeasurmentCross-checkWithCamera_rotated_F.txt", "a") as myfile:myfile.writelines(L)
    n=0
    y=222.6
    for i in range(20):
        #touch(2,65+3,5)
        #h=random.randint(0, 80)/1000.0
        #h=0.3-0.035+h
        #h=round(h,3)
        #h=random.randint(300-15, 300+15)/1000.0
        #h=round(h,3)
        #print("h>>>>>>>>",h)
        laser=LaserSensor.GotoXYZ(machine,127.1,y,0.3)
		machine_pos=laser-0.3
        takePicture(n)
        
        x_,y_,z_2=machine.probe_z(speed=5, up_rel=0.2)
        gap=z_2-machine_pos
        
        now = datetime.now()				
        L=[str(n),"\t",now.strftime("%H:%M:%S"),"\t",str(127.1),"\t",str(y),"\t",str(0.3),"\t",str(z_2),"\t",str(laser),"\t",str(machine_pos),"\t",str(gap),"\n"]				
        with open("gapMeasurmentCross-checkWithCamera_0_test.txt", "a") as myfile:myfile.writelines(L)
        print(touch,laser,machine_pos,gap)
        n=n+1
        #random.randint(0, 12)/1000.0
        y=round(y+0.484-0.097,3)
    #file5.close()
    exit()
    #repeat height measurement above x, y <<<

	
    #repeat height measurement above x, y >>>
    file5 = open('heightMeasurmentCompareOnSensorSamePoint_gapAndSpeedChanged_0.7.txt',"w")
    n=0
    for i in range(10):
        #touch(2,65+3,5)
        laser=LaserSensor.GotoXYZ(machine,37,115,0.7)
        now = datetime.now()				
        L=[str(n),"\t",now.strftime("%H:%M:%S"),"\t",str(37),"\t",str(115),"\t",str(touch),"\t",str(laser),"\t",str(diff),"\t",str(gap),"\n"]				
        file5.writelines(L)
        print(touch,laser,diff,gap)
        n=n+1
    file5.close()
    exit()
    #repeat height measurement above x, y <<<


    
    #machine.gotoxy(30,65+45)
    
    #Height measurement above sensor jig and sensor  >>>
    n=0
    cnd=True
    file4 = open('heightMeasurmentCompareOnSensorPhaseI_V2.1_gapAndSpeedChanged.txt',"w")
    
    LX=np.linspace(37,37+75-6,10,endpoint=True)#Sensor:37+55
    LY=np.linspace(115,115+70+6,10,endpoint=True)#sensor:110+70 
    
    for lx in LX:
        for ly in LY:
            laser=LaserSensor.GotoXYZ(machine,round(lx,3),round(ly,3),0.2) 
            print(n,round(lx,3),round(ly,3),touch,laser,diff,gap)
            now = datetime.now()				
            L=[str(n),"\t",now.strftime("%H:%M:%S"),"\t",str(round(lx,3)),"\t",str(round(ly,3)),"\t",str(touch),"\t",str(laser),"\t",str(diff),"\t",str(gap),"\n"]				
            file4.writelines(L)		
            n=n+1
            if n>=200:cnd=False	
    file4.close()
    exit()
	
	#Height measurement above sensor jig and sensor  >>>
	#1D array above kapton >>>
    n=0
    cnd=True
    file3 = open('heightMeasurmentCompareOnKapton_v2_gapAndSpeed_changed.txt',"w")
    while cnd:
        LY=random.randint(110000, 110000+80000)/1000.0#np.linspace(116.5,116.5+56,4,endpoint=True)
        laser=LaserSensor.GotoXYZ(machine,30,round(LY,3),0.2) 
        print(n,round(LY,3),touch,laser,diff,gap)
        now = datetime.now()				
        L=[str(n),now.strftime("%H:%M:%S"),"\t",str(round(LY,3)),"\t",str(touch),"\t",str(laser),"\t",str(diff),"\t",str(gap),"\n"]				
        file3.writelines(L)		
        n=n+1
        if n>=100:cnd=False	
    file3.close()	
    exit()
    #1D array above kapton <<<	
	#2D array above kapton JIG >>>
    n=0
    cnd=True
    file2 = open('heightMeasurmentCompareOnKaptonJig.txt',"w")
    while cnd:
        LX=np.linspace(39,39+75,4,endpoint=True)
        LY=np.linspace(116.5,116.5+56,4,endpoint=True)
        for lx in LX:
            for ly in LY:
                laser=LaserSensor.GotoXYZ(machine,round(lx,3),round(ly,3),0.1) 
                print(n,round(lx,3),round(ly,3),touch,laser,diff,gap)
                now = datetime.now()				
                L=[str(n),now.strftime("%H:%M:%S"),"\t",str(round(lx,3)),"\t",str(round(ly,3)),"\t",str(touch),"\t",str(laser),"\t",str(diff),"\t",str(gap),"\n"]				
                file2.writelines(L)		
                n=n+1
                if n>=200:cnd=False	
    file2.close()
    exit()
    #2D array above kapton JIG <<<
	#1D array above kapton >>>
    n=0
    cnd=True
    file3 = open('heightMeasurmentCompareOnKapton_v2_gapAndSpeed_changed.txt',"w")
    while cnd:
        LY=random.randint(110000, 110000+80000)/1000.0#np.linspace(116.5,116.5+56,4,endpoint=True)
        laser=LaserSensor.GotoXYZ(machine,30,round(LY,3),0.2) 
        print(n,round(LY,3),touch,laser,diff,gap)
        now = datetime.now()				
        L=[str(n),now.strftime("%H:%M:%S"),"\t",str(round(LY,3)),"\t",str(touch),"\t",str(laser),"\t",str(diff),"\t",str(gap),"\n"]				
        file3.writelines(L)		
        n=n+1
        if n>=10:cnd=False	
    file3.close()	
    exit()
    #1D array above kapton <<<
    

    #repeat height measurement above x, y >>>
    for i in range(10):
        #touch(2,65+3,5)
        laser=LaserSensor.GotoXYZ(machine,2,65+3,0.2)
        print(touc,laser,diff,gap)
    exit()
    #repeat height measurement above x, y <<<

	
	#repeatability on calibration point >>>
    n=0
    file3=open('repeatibilityOnCalibrationPoint.txt',"w")
    for i in range(100):
        laser=LaserSensor.GotoXYZ(machine,round(0,3),round(65+40,3),0.1) 
        print(n,round(0,3),round(65+40,3),touch,laser,diff)
        now = datetime.now()				
        L=[str(n),"\t",now.strftime("%H:%M:%S"),"\t",str(round(0,3)),"\t",str(round(65+40,3)),"\t",str(touch),"\t",str(laser),"\t",str(diff),"\n"]				
        file3.writelines(L)		
        n=n+1
    file3.close()
    exit()
	#repeatability on calibration point <<<
	
    #repeat height measurement above x, y >>>
    for i in range(10):
        #touch(2,65+3,5)
        laser=LaserSensor.GotoXYZ(machine,30,140.758,0.2)
        print(touc,laser,diff,gap)
    exit()
    #repeat height measurement above x, y <<<    

    
    for i in range(10):
        print("0,0")
        machine.gotoxy(0,0)
        machine.down(39)
        machine.probe_z(speed=25, up_rel=0.1)
        time.sleep(2)
        machine.down(10)
		
        print("0,65")
        machine.gotoxy(0,65)
        machine.down(40-3)
        machine.probe_z(speed=25, up_rel=0.1)
        time.sleep(2)
        machine.down(10)
		
        print("60,140")
        machine.gotoxy(60,95+45)
        machine.down(24)
        machine.probe_z(speed=25, up_rel=0.1)
        time.sleep(2)
        machine.down(10)
    exit()
    
    
        #neddle position finding by camera >>>
    x=127.4
    y=221.1
    z=21.4
    step=1
    while True:
        print("x",x,"y",y,"z",z,"step",step)
        machine.gotoxy(x,y)
        machine.down(z)
        status,img=vc.read()
        cv2.imshow("img",img)
        img=cv2.Canny(img,25,50)
        cv2.imshow("canny",img)
        key = cv2.waitKey(1)
        #step=0.5
        if key==27:    # Esc key to stop
            break
        elif key==-1:  # normally -1 returned,so don't print it
           continue
        elif key==119:#y+ w
            y=y+step
        elif key==115:#y- s
            y=y-step
        elif key==100:#x+ d
            x=x+step
        elif key==97:#x- a
            x=x-step
        elif key==102:#z+ f
            z=z+step
        elif key==99:#z- c
            z=z-step
        elif key==61:#step+ +
            step=step+0.1
            step=round(step,3)
        elif key==45:#step- -
            step=step-0.1
            step=round(step,3)
        
        else:
            print (key) # else print its value
    #neddle position finding by camera <<<  
    """
    #x_,y_,z_=touch(x=0,y=65,aprxHightOfObject=2)
    #LaserSensorGotoXYZ(machine,x_,y_,z_-5)
    
	
	#exit()
    #machine.gotoxy(0,66)
    #for i in range(10):
    #    machine.down(40)
    #    x_,y_,z_=machine.probe_z(speed=25, up_rel=0.1)
    #    print("0.1:",x_,y_,z_)
    #machine.down(39)
    #x_,y_,z_=machine.probe_z(speed=25, up_rel=0.5)
    #print("0.5:",x_,y_,z_)
    #sleep(2)
    #exit()
    
	
    #machine.gotoxy(0,0)
    #machine.down(1)	
    #exit()
    
    #file1 = open('result_compare_laser_machine_1.txt',"w")
    #L_Z=np.linspace(42,42-20,20,endpoint=False)
    #for i in L_Z:
    #    machine.down(round(i,3))
    #    sleep(1)
    #    L=[str(round(i,3)),"\t",str(LaserSensor.Height()),"\t",str(LaserSensor.Valid()),"\n"]
    #    file1.writelines(L)
    #    print(round(i,3),LaserSensor.Height(),LaserSensor.Valid())
    #file1.close()
    #exit()
	
	
	
    #edge
    #machine.gotoxy(0,66)
	
    #machine.down(42)
    #exit()

	#go close and touch it
    
    #machine.down(2)
    #machine.gotoxy(32+11-4+,83+29+4.5)
    #exit()
	#Hey nesf mikone faseleh ro>>>>>		
    #LaserSensor.GotoXYZ(machine,200-70-4+0.5+33+1.2,200-62,0.05)
    """
	file1 = open('heightMeasurmentCompare',"w")
    L=["Time","\t","laser sensor","\t","Touch sensor","\t","Gap","\n"]
    file1.writelines(L)
    gap=10
    for i in range(15):
        #LaserSensor.GotoXYZ(machine,20,95,0.1)
        h=LaserSensor.GotoXYZ(machine,0,83,gap)
        x_,y_,z_=machine.probe_z(speed=25, up_rel=0.2)
        now = datetime.now()
        L=[now.strftime("%H:%M:%S"),"\t",str(h),"\t",str(z_),"\t",str(gap),"\n"]
        print(now.strftime("%H:%M:%S"),h,z_,gap)
        file1.writelines(L)
        time.sleep(1)
        machine.down(10)
        time.sleep(1)
        gap=round(gap/2.0,3)
        print("gap= ",gap)
        if gap==0.001:
            gap=gap-0.001
        else:
            gap=round(gap/2.0,3)
        #LaserSensor.GotoXYZ(machine,29.3,120,0.1)
        #LaserSensor.GotoXYZ(machine,60,95+50,0.1)
        #LaserSensor.GotoXYZ(machine,200,200,0.1)
    file1.close()
    exit()
	#Hey nesf mikone faseleh ro<<<<<
	"""
	
    #for i in range(10):
    #    print(LaserSensor.Height())
    #machine.down(z_-15)
    #machine.gotoxy(0-LaserSensor.get_dx0()+LaserSensor.dx(LaserSensor.Height()),66-LaserSensor.get_dy0()+LaserSensor.dy(LaserSensor.Height())) #corrected point
    #print("5: ",LaserSensor.Height())
    #L_Z=np.linspace(23,21,20,endpoint=False)     #-y direc
    #for p in L_Z:
    #    machine.down(p)
    #    print (p,LaserSensor.Valid())
    	#sleep(2)
    #exit()
    #LaserSensor.Calibration() 
	
	
	
	
	
    #machine.down(z_-10)# bordamesh bala
    #machine.gotoxy(0-LaserSensor.get_dx0(),66-LaserSensor.get_dy0())# laser bere balaye on noghteh
    #machine.down(z_)# bereh hamon ertefa
    #exit()	
    winsound.Beep(2500, 2)
    file1 = open('result_mAndB_new_per_x.txt',"w")
    L=["time","\t","machine position","\t","laser sensor height","\t","detected edge","\n"]
    file1.writelines(L)
    Y=[]
    Z=[]
    x_,y_,z_=TouchSurf(x=0,y=65,aprxHightOfObject=2.5,speed=5)# touch(,0,65,aprxHightOfObject=2.5,speed=5)
    L_Z=np.linspace(z_-6,z_-16,10,endpoint=False)     #-y direc
    n=0
    for p in L_Z:
        machine.down(round(p,3))
        #machine.gotoxy(0-LaserSensor.get_dx0(),66-LaserSensor.get_dy0())
        height=LaserSensor.Height()
        dy_corrected=LaserSensor.dy(LaserSensor.Height())
        machine.gotoxy(0-LaserSensor.get_dx0(),65-LaserSensor.get_dy0())
		
		
        height=LaserSensor.Height()
        #sleep(2)
        winsound.Beep(2000, 1)
        print(dy_corrected)
        edge=LaserPosition_Y(0-LaserSensor.get_dx0(),65-LaserSensor.get_dy0())#+dy_corrected,z_)
        #edge=LaserPosition_X(-5-LaserSensor.get_dx0(),65-LaserSensor.get_dy0())
        print(n,"@@@@@@>>>>>>>  ",round(p,3),height,edge,"<<<<<<<<<<")
        Z.append(height)
        Y.append(edge)

        now = datetime.now()
        L=[now.strftime("%H:%M:%S"),"\t",str(p),"\t",str(height),"\t",str(edge),"\n"]
        file1.writelines(L)
        n+=1
         
    print(Y)
    print(Z)
    m,b=np.polyfit(Z,Y,1)
    print(m,b)
    

#    for i in range(20):
#        L=[str(i),"\t",str(Y[i]),"\t",str(Z[i]),"\n"]	
#        file1.writelines(L)
    L=["m:","\t",str(m),"\t","b:","\t",str(b),"\n"]	
    file1.writelines(L)
    m,b=np.polyfit(L_Z,Y,1)
    L=["m:","\t",str(m),"\t","b:","\t",str(b),"\n"]	
    file1.writelines(L)
    print(m,b)
    file1.close()
	
	
	
	
	
	
    """
    ine_test=np.linspace(0,1,50,endpoint=True)
    acc=0
    for i in ine_test:
        acc=acc+round(i,3)
        machine.gotoxy(0,acc)
        print(acc)
        sleep(0.5)
    """    
	

    """
    machine.gotoxy(LaserSensor.dx(), LaserSensor.dy())
    print("init finished")
    
    

	print("goto " ,LaserSensor.dx(), LaserSensor.dy()," finished")
    machine.down(42-2.5)
    table_h = machine.probe_z(speed=25, up_rel=0.0)
    print("probe finished",table_h)
    print("height",table_h[2])
    
    print("H: ",LaserSensor.Height())
    machine.down(10)
    
    machine.gotoxy(0,0)
    machine.down(table_h[2])

    LaserSensor.Calibration()
    print("H: after calibration ",LaserSensor.Height())

	
	
	
	
	
	
	
	
	
    machine.down(42-15)
    machine.gotoxy(0,30)	

    print("H above jig: ",LaserSensor.Height())
    machine.gotoxy(LaserSensor.dx(),LaserSensor.dy()+30)
	
    table_h = machine.probe_z(speed=25, up_rel=0.1)
    print("probe finished",table_h)

    LaserSensor.Calibration()
    machine.down(10)

	
	
    file1 = open('result_test.txt',"w")
    for hh in range(10):
        machine.gotoxy(0,30)	
        machine.down(table_h[2])
        
        upperEdge=random.randint(3200, 3600)/100.0#30#edge+margin
        lowerEdge=upperEdge-15#random.randint(1800, 2300)/100#upperEdge-10#edge-margin
        UE=upperEdge
        LE=lowerEdge
        condition=True
        r=[0,0,0]
        k=0
        m=0
        threshould_edge=5
        pre_up_Edge,pre_down_Edge=0,0
        part=0
        detected_edge=0
        while condition:
            line_test=np.linspace(lowerEdge,upperEdge,3,endpoint=True)
            for j in line_test:
                machine.gotoxy(0,(round(j,3)))
                sleep(0.1)
                
                r[k]=LaserSensor.Height()
                k+=1
            k=0
            print(r,line_test,upperEdge-lowerEdge)
     
            if abs(abs(r[0])-abs(r[1]))>threshould_edge:
                lowerEdge=round(line_test[0],3)#-0.01
                upperEdge=round(line_test[1],3)#+0.01
                part=1
            elif abs(abs(r[1])-abs(r[2]))>threshould_edge:
                lowerEdge=round(line_test[1],3)#-0.01
                upperEdge=round(line_test[2],3)#+0.01
                part=2
            else:
                lowerEdge=LE
                upperEdge=UE+1
                
                print("Err",m,r,line_test)
                m+=1
                
     
                
                #if part==1:
                #    lowerEdge=upperEdge-0.01
                #    upperEdge=upperEdge+(upperEdge-lowerEdge)+0.01
                #elif part==2:
                #    lowerEdge=lowerEdge-(upperEdge-lowerEdge)-0.01
                #    upperEdge=lowerEdge
				
                if m>5:
                    condition=False
                    m=0
                    now = datetime.now()
                    L=[str(hh),"\t",now.strftime("%H:%M:%S"),"\t","Kehft shod","\t",str(LE),"\t",str(UE),"\n"]
                    file1.writelines(L)
                
            if upperEdge -lowerEdge <0.7:
                fine_line=np.linspace(upperEdge,lowerEdge,14,endpoint=True)
                h_0=LaserSensor.Height()
                print("h0",h_0)
                for fine_step in fine_line:
                    machine.gotoxy(0,round(fine_step,3))
                    print("moved to ",round(fine_step,3),LaserSensor.Height())					
                    if abs(LaserSensor.Height()-h_0)>threshould_edge:
                        detected_edge=round(fine_step,3)
                        print("detecteeeed >>>>",detected_edge)
                        condition=False
                        now = datetime.now()
                        L=[str(hh),"\t",now.strftime("%H:%M:%S"),"\t",str('%5.3f' %(detected_edge)),"\t",str(LE),"\t",str(UE),"\n"]
                        file1.writelines(L)
                        break
					
					

            if upperEdge-lowerEdge<0.100:
                detected_edge=lowerEdge
                print(">>>>>>>>>>>",detected_edge)
                now = datetime.now()
                L=[str(hh),"\t",now.strftime("%H:%M:%S"),"\t",str('%5.3f' %(detected_edge)),"\t",str(LE),"\t",str(UE),"\n"]
                file1.writelines(L)        
                condition=False
    """
            
        
    print("finished")
    #file1.close()
    		
	
	
	
	
	
	
	
	
	
    """
    time.sleep(1)
    Condition=True
    step=0
    while Condition: #course move to be in range
        if LaserSensor.Valid()=='0':
            print(LaserSensor.Valid(),LaserSensor.Height(),Condition)
            machine.down(step)
            step+=5
        else:
            Condition=False
    Condition=True
    print("Next step")    
    while Condition: #fine move to touch
        h=LaserSensor.Height()
        print(h,Condition)
        machine.down(step)
        step+=0.2
        if h<=8.5:
            Condition=False
    #LaserSensor.Calibration()
    #machine.down(30)
    print("finished...")  
                        
        
    
    #print(LaserSensor.Height())
    #machine.gotoxy(SCALE_POSITION[0], SCALE_POSITION[1])
    
    #machine.down(35)
    #print(LaserSensor.Height())
    # metallic pink
    #table_h = machine.probe_z(speed=25, up_rel=0.5) #0.1
    #table_h = machine.probe_z(speed=100, up_rel=0.5) #0.3 
    
    # plastic pink
    #time.sleep(2)
    
    #table_h = machine.probe_z(speed=25, up_rel=0.1)#0.1
    #print(table_h)
    #print(LaserSensor.Height())
    #table_h = machine.probe_z(speed=100, up_rel=0.6) #0.37
    
    
    #print('Read loading cell and scale value')
    #print('Should be relatively close')
    
    #machine.down(scale_h - 1)
    #machine.down(scale_h + 0.05, speed=25)
    """
    
