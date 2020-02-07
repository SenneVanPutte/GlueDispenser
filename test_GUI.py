from PyQt4 import QtGui, QtCore
import sys
import time

#finished = QtCore.pyqtSignal()
#class Worker(QtCore.QObject):
class WorkerSignals(QtCore.QObject):
	finished = QtCore.pyqtSignal()

class Worker(QtCore.QRunnable):
	def __init__(self, function):
		print('init worker')
		super(Worker, self).__init__()
		self.signals = WorkerSignals()
		self.function = function

	def run(self):
		print('run worker')
		self.function()
		self.signals.finished.emit()

class Second(QtGui.QWidget):
    def __init__(self, parent=None):
		print('Constructing')
		super(Second, self).__init__(parent)
		print('adding grid')
		self.grid = QtGui.QGridLayout()
		#self.setCentralWidget(self.grid)
		self.setLayout(self.grid)
		self.pushButton = QtGui.QPushButton("click me 2")
		self.grid.addWidget(self.pushButton, 0, 0, 1, 2)
		
		self.show()
		print('grid added')

#QMainWindow
#QWidget
class First(QtGui.QWidget):
	def __init__(self, parent=None):
		super(First, self).__init__(parent)
		self.setGeometry(50, 50, 1000, 400)
		
		#self.thread = QtCore.QThread(self)
		self.pool = QtCore.QThreadPool()

		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		
		self.pushButton = QtGui.QPushButton("click me")
		self.grid.addWidget(self.pushButton, 0, 0)
		self.pushButton.clicked.connect(self.on_pushButton_clicked)
		self.dialogs = list()
		#self.show()
		
		self.pushButton1 = QtGui.QPushButton("worker 1")
		self.grid.addWidget(self.pushButton1, 1, 0)
		self.pushButton1.clicked.connect(lambda: self.thread_worker(lambda: self.spam('worker1')))
		#self.pushButton1.clicked.connect(lambda: self.spam('worker1'))
		
		self.pushButton2 = QtGui.QPushButton("worker 2")
		self.grid.addWidget(self.pushButton2, 1, 1)
		self.pushButton2.clicked.connect(lambda: self.thread_worker(lambda: self.spam('worker2')))
		#self.pushButton2.clicked.connect(lambda: self.spam('worker2'))

	def on_pushButton_clicked(self):
		#self.hide()
		dialog = Second()
		self.dialogs.append(dialog)
		print('showing')
		#dialog.show()
		
	def spam(self, text):
		for i in range(10):
			print(text)
			time.sleep(0.5)

	
	def thread_worker(self, function):
		print(self.thread)
		self.toggle(False)
		worker = Worker(function)
		#worker.moveToThread(self.thread)
		worker.signals.finished.connect(self.worker_finished)
		#self.thread.started.connect(worker.run)
		print('starting thread')
		#self.thread.start()
		self.pool.start(worker)
		print('started thread')
		return
		
	def toggle(self, bool):
		self.pushButton1.setEnabled(bool)
		self.pushButton2.setEnabled(bool)
	
	def worker_finished(self):
		self.toggle(True)
		


#def main():
    

if __name__ == '__main__':
	
	app = QtGui.QApplication(sys.argv)
	main = First()
	main.show()
	sys.exit(app.exec_())
