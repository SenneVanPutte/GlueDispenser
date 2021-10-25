import serial
import time
import sys
import math
import datetime
import numpy as np
from datetime import datetime
class LaserSensor():
    CalibrationCoefficient=30
    dx0=39.650##rotated:39.23#per:39.07
    dy0=64.475#rotated:53.05#per:64.16
    needle_xy=[0,0]
    laser_xy=[0,0]
	
    thetaX=0#0.013#0.0129degree
    thetaY=0#0.17#9.648degree
    def __init__(self,PortName):
        self.PortName=PortName
        self.Baudrate=115200
        self.serial=serial.Serial(self.PortName,115200)
        #try:
            
            #return 1#,"The port is openned succesfully"
        #except IOError:
            #return 0#,"Problem in openning the port"
    #def init(self,PortName):
    #    try:
    #        ser = serial.Serial(PortName,115200)
    #        return 1,"The port is openned succesfully"
    #    except IOError:
    #        return 0,"Problem in openning the port"
   
    def Height(self):
        time.sleep(0.1)
        self.serial.write(b's')
        return round(float(self.CalibrationCoefficient)-float(self.serial.readline().decode().strip()),3)
    def HeightAt(self,machine,x,y):
        machine.down(10)
        machine.gotoxy(float(x)-self.get_dx0(),float(y)-self.get_dy0())
        step=10
        condition=True
        while (int(self.Valid())==0):
            step+=5
            machine.down(step)

        machine.gotoxy(float(x)-self.get_dx0()+self.dx(self.Height()),float(y)-self.get_dy0()+self.dy(self.Height()))
        return step+self.Height()
    def GotoXYZ(self,machine,x,y,z):
        height_=self.HeightAt(machine,x,y)
        machine.down(10)
        machine.gotoxy(float(x),float(y))
        machine.down(height_-z)
        return height_
    def EdgeDetection(self,machine,StartPoint_xy,ScanningRange,Direction,NeedleOrLaser,aprxHightOfObject,ToolsWidth=0):
        print('About to move for edge detection')
        #machine.gotoxy(20,20)
        #return 0
        #exit()
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
            #print("line:::",line_test)
            for k,j in enumerate( line_test):
                
                if NeedleOrLaser=='Needle':
                    if Direction=='x':
                        machine.gotoxy(round(j,3),StartPoint_xy[1])
                    if Direction=='y':
                        machine.gotoxy(StartPoint_xy[0],round(j,3))
                    machine.down(42-aprxHightOfObject)
                    r[k]=machine.probe_z(speed=50, up_rel=0.5)[2]
                    machine.down(42-aprxHightOfObject)
                if NeedleOrLaser=='Laser':
                    if Direction=='x':
                        machine.gotoxy(round(j,3),StartPoint_xy[1])
						#machine.gotoxy(round(j,3)-self.get_dx0()+self.dx(self.Height()),StartPoint_xy[1]-self.get_dy0()+self.dy(self.Height()))
                    if Direction=='y':
                        machine.gotoxy(StartPoint_xy[0],round(j,3))
						#machine.gotoxy(StartPoint_xy[0]-self.get_dx0()+self.dx(self.Height()),round(j,3)-self.get_dy0()+self.dy(self.Height()))
                    machine.down(24)
                    r[k]=self.Height()
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
                h_0=machine.probe_z(speed=20, up_rel=0.5)[2] if NeedleOrLaser=='Needle' else self.Height()
                for fine_step in fine_line:
                    if NeedleOrLaser=='Laser':
                        if Direction=='x':
                            machine.gotoxy(round(fine_step,3),StartPoint_xy[1])
							#machine.gotoxy(round(fine_step,3)-self.get_dx0()+self.dx(self.Height()),StartPoint_xy[1]-self.get_dy0()+self.dy(self.Height()))
                        if Direction=='y':
                            machine.gotoxy(StartPoint_xy[0],round(fine_step,3))
							#machine.gotoxy(StartPoint_xy[0]-self.get_dx0()+self.dx(self.Height()),round(fine_step,3)-self.get_dy0()+self.dy(self.Height()))
                    if NeedleOrLaser=='Needle':
                        if Direction=='x':
                            machine.gotoxy(round(fine_step,3),StartPoint_xy[1])
                        if Direction=='y':
                            machine.gotoxy(StartPoint_xy[0],round(fine_step,3))
                    
                    new_value=machine.probe_z(speed=50, up_rel=0.5)[2] if NeedleOrLaser=='Needle' else self.Height()#max_z=42-aprxHightOfObject+1.2
                    
                    if abs(new_value-h_0)>threshould_edge:
                        detected_edge=round(fine_step,3)
                        print("Detected edge: ",detected_edge)
                        condition=False
                        machine.down(10)
                        #if NeedleOrLaser=='Laser':
                        #    if Direction=='x': Laser.
                        if NeedleOrLaser=='Laser':
                            if Direction=='x':
                                detected_edge=detected_edge#-self.get_dx0()+self.dx(self.Height())
                            if Direction=='y':
                                detected_edge=detected_edge#-self.get_dy0()+self.dy(self.Height())
                        if NeedleOrLaser=='Needle':
                            detected_edge=detected_edge+ToolsWidth/2.0 
                        return detected_edge
                        break
	
    def EdgeDetection_InNeedleCoordination(self,machine,StartPoint_xy,ScanningRange,Direction,aprxHightOfObject):
        detected_edge=self.EdgeDetection(machine,StartPoint_xy,ScanningRange,Direction,'Laser',aprxHightOfObject,ToolsWidth=0)
        if Direction=='x':
            return detected_edge+self.dx0
        if Direction=='y':
            return detected_edge+self.dy0

	
	"""
	def GotoXYZ(self,machine,x,y,z):
        machine.down(10)
        machine.gotoxy(float(x)-self.get_dx0(),float(y)-self.get_dy0())
        step=10
        condition=True
        while (int(self.Valid())==0):
            step+=5
            machine.down(step)

        machine.gotoxy(float(x)-self.get_dx0(),float(y)-self.get_dy0()+self.dy(self.Height()))
        height_corrected=self.Height()
        machine.down(10)
        machine.gotoxy(float(x),float(y))
        machine.down(step+height_corrected-z)
        return height_corrected,step+height_corrected-z
    def HeightAt(self,machine,x,y):
        machine.down(10)
        machine.gotoxy(float(x)-self.get_dx0(),float(y)-self.get_dy0())
        step=10
        condition=True
        while (int(self.Valid())==0):
            step+=5
            machine.down(step)

        machine.gotoxy(float(x)-self.get_dx0()+self.dx(self.Height()),float(y)-self.get_dy0()+self.dy(self.Height()))
        height_corrected=self.Height()
        #machine.down(10)
        #machine.gotoxy(float(x),float(y))
        #machine.down(step+height_corrected-z)
        return height_corrected#,step+height_corrected-z

	"""   
    def Temp(self):
        self.serial.write(b't')
        return float(self.serial.readline().decode().strip())

    def DigitalOutput(self):
        self.serial.write(b'p')
        return self.serial.readline().decode().strip()
    
    def Calibration(self,default_height=0,bent=0):
        self.serial.write(b's')
        self.CalibrationCoefficient=float(self.serial.readline().decode().strip())+float(default_height)-float(bent)#-0.1
        return 1,"Done"

    def LaserOff(self):
        self.serial.write(b'0')
        return self.serial.readline().decode().strip()

    def LaserOn(self):
        self.serial.write(b'1')
        return self.serial.readline().decode().strip()

    def help(self):
        self.serial.write(b'?')
        n=int(self.serial.readline().decode().strip())
        str=""
        for i in range(n):
            str=str+self.serial.readline().decode().strip()+'\n'
        time.sleep(0.5)
        return str
     
    def HighThreshold(self):
        self.serial.write(b'h')
        return self.serial.readline().decode().strip()

    def LowThreshold(self):
        self.serial.write(b'l')
        return self.serial.readline().decode().strip()

    def Valid(self):
        self.serial.write(b'v')
        return self.serial.readline().decode().strip()

    def LcdZero(self):
        self.serial.write(b'r')
        return self.serial.readline().decode().strip()

    def LcdZeroCancel(self):
        self.serial.write(b'c')
        return self.serial.readline().decode().strip()

    def get_dx0(self):
        return self.dx0
		
    def set_dxy0(self,x0,y0): 
        self.dx0=x0
        self.dy0=y0
		
    def get_dy0(self):
        return self.dy0

    def dx(self,height):
        return round(self.thetaX*height,3)

    def dy(self,height):
        return round(self.thetaY*height,3)#3.9
    def Setneedle_x(self,x):
        self.needle_xy[0]=x
		
    def Setneedle_y(self,y):
        self.needle_xy[1]=y
		
    def Setlaser_x(self,x):
        self.laser_xy[0]=x
		
    def Setlaser_y(self,y):
        self.laser_xy[1]=y

		
    def SetXYOffset(self,LaserXY,NeedleXY):
        self.dx0=NeedleXY[0]-LaserXY[0]
        self.dy0=NeedleXY[1]-LaserXY[1]
    def TouchSurf(self,machine,x,y,aprxHightOfObject=2,speed=5):
        machine.down(10)
        machine.gotoxy(x,y)
        machine.down(42-aprxHightOfObject)
        z_=machine.probe_z(speed=5, up_rel=0.1)[2]
        machine.down(z_-10) #needle go to safe height
        return z_ 
    def ZCalibration(self,machine,x,y,aprxHightOfObject=24):
        z_touch=[0]*1
        for i in range(1):
            z_touch[i]=self.TouchSurf(machine,float(x),float(y),aprxHightOfObject,speed=20)   #needle go to x,y and touch the surface to measure height by touch sensor =>z_
        z_=	np.mean(z_touch)
        print("average of touch",z_)
        print("std of touch",np.std(z_touch),"max-min",np.max(z_touch)-np.min(z_touch))
        machine.gotoxy(x-self.get_dx0(),y-self.get_dy0())                 #Laser 
        #machine.down(z_)	                                              #Laser go to same height as surface was
        do_calibration_at_different_height=5                              #offset of height to do calibration (for valid data)
                               
        machine.down(z_-do_calibration_at_different_height)	              #move machine to height
        machine.gotoxy(x-self.get_dx0()+self.dx(do_calibration_at_different_height),y-self.get_dy0()+self.dy(do_calibration_at_different_height)) #correct x,y base on height
        self.Calibration(default_height=do_calibration_at_different_height,bent=0.0)              #Laser calibration
        """
		LZ=np.linspace(z_-5,z_-14,5,endpoint=True)#Sensor:37+55
        name="calibration result by machine.txt"
        L=["Z","\t","Time","\t","Height by machine(z_-lz)","\t","Laser","\t","difference","\n"]				
        with open(name, "a") as myfile:myfile.writelines(L)
        print("SM","\t","Sensor","\t","Diff")
        loadcell=[]
        laser=[]
        for lz in LZ:
            machine.down(lz)
            machine.gotoxy(x-self.get_dx0()+self.dx(self.Height()),y-self.get_dy0()+self.dy(self.Height()))
            L=[str(lz),"\t",datetime.now().strftime("%H:%M:%S"),"\t",str(round(z_-lz,3)),"\t",str(self.Height()),"\t",str(round(z_-lz-self.Height(),3)),"\n"]				
            with open(name, "a") as myfile:myfile.writelines(L)
            hh=self.Height()
            loadcell.append(round(z_-lz,3))
            laser.append(self.Height())
            print(round(z_-lz,3),"\t",hh,"\t",round(z_-lz-hh,3),self.Valid())
        m,b=np.polyfit(loadcell,laser,1)
        print(m,b)
        L=["m:","\t",str(round(m,3)),"\t","b","\t",str(round(b,3)),"\n"]				
        with open(name, "a") as myfile:myfile.writelines(L)
        if abs(b)>=0.025:
            machine.down(z_-5)
            self.Calibration(default_height=5,bent=0.0+b)
            print("SM","\t","Sensor","\t","Diff")
            loadcell_=[]
            laser_=[]
            for lz in LZ:
                machine.down(lz)
                machine.gotoxy(x-self.get_dx0()+self.dx(self.Height()),y-self.get_dy0()+self.dy(self.Height()))
                L=[str(lz),"\t",datetime.now().strftime("%H:%M:%S"),"\t",str(round(z_-lz,3)),"\t",str(self.Height()),"\t",str(round(z_-lz-self.Height(),3)),"\n"]				
                with open(name, "a") as myfile:myfile.writelines(L)
                hh=self.Height()
                loadcell_.append(round(z_-lz,3))
                laser_.append(hh)
                print(round(z_-lz,3),"\t",hh,"\t",round(z_-lz-hh,3))
            m,b=np.polyfit(loadcell_,laser_,1)
            print(m,b)
            L=["m:","\t",str(round(m,3)),"\t","b","\t",str(round(b,3)),"\n"]				
            with open(name, "a") as myfile:myfile.writelines(L)
            L=["##------------------------------------------------##\n"]				
            with open(name, "a") as myfile:myfile.writelines(L)
        """
        machine.down(10)
        print("Z calibration had been finished!!!")


	#@classmethod
    #def calibration(cls):
    #    cls.CalibrationCoefficient=10
