from serial import Serial
import io
from threading import Thread
import signal
tg = Serial("COM3", 115200, xonxoff=True,timeout=0.5)
#ser = serial.serial_for_url('loop://', timeout=1)
tinyg = io.TextIOWrapper(io.BufferedRWPair(tg, tg))
kill=0

def emergency_stop(signal, frame):
	#global machine
	global kill
	print "Emergency Stop sequence"
	#machine.stop()
	kill=1
	exit(0)
	
signal.signal(signal.SIGINT, emergency_stop)


def readState():
	print "reading thread alive"
	global kill
	while not kill:
		st=tinyg.readline()
		if st:print st
		#print st
readthread = Thread(target=readState)
readthread.start()
tinyg.write(unicode("$ex=1\n"))
tinyg.flush()
tinyg.write(unicode("$ej=1\n"))
tinyg.flush()
tinyg.write(unicode("$ec=0\n"))
tinyg.flush()
tinyg.write(unicode("$ee=1\n"))
tinyg.flush()
tinyg.write(unicode("$jv=3\n"))
tinyg.flush()
tinyg.write(unicode("$js=1\n"))
tinyg.flush()
tinyg.write(unicode("""{"gc":"G28.2 X0 Y0 Z0"}\n"""))
tinyg.flush()

while True:
	x = raw_input("send tinyg a command ")
	if x:
		st="""{{"gc":"{}"}}\n""".format(x)
		print st
		tinyg.write(unicode(st))
		tinyg.flush()
readthread.stop()