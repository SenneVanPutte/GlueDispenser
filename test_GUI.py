from PyQt4 import QtGui, QtCore
import sys


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
		self.pushButton = QtGui.QPushButton("click me")

		self.grid = QtGui.QGridLayout()
		self.setLayout(self.grid)
		self.grid.addWidget(self.pushButton, 0, 0, 1, 2)
		#self.setCentralWidget(self.pushButton)

		self.pushButton.clicked.connect(self.on_pushButton_clicked)
		self.dialogs = list()
		#self.show()

    def on_pushButton_clicked(self):
        #self.hide()
        dialog = Second()
        self.dialogs.append(dialog)
        print('showing')
        #dialog.show()


#def main():
    

if __name__ == '__main__':
	
	app = QtGui.QApplication(sys.argv)
	main = First()
	main.show()
	sys.exit(app.exec_())