import sys
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
#from PyQt4.QtWidgets import *
from PyQt4.QtCore import *

### global variables 
# global memorysize                                          # ---
# global numberofholes                                       # ---
###        


class Window(QWidget):
    def __init__(self,parent=None):
        super(Window,self).__init__(parent)
        self.setWindowTitle("Memory 1")
        self.setGeometry(50, 50, 500, 300)
        self.home()

    def home(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.memory = QLabel(self)
        self.memory.setText("Total Memory size")
        self.grid.addWidget(self.memory, 0, 0)

        self.memoryinput = QLineEdit(self)
        self.grid.addWidget(self.memoryinput, 0, 20)

        self.holes = QLabel(self)
        self.holes.setText("Number of holes")
        self.grid.addWidget(self.holes, 5, 0)

        self.inputholes = QLineEdit(self)
        self.grid.addWidget(self.inputholes, 5, 20)

        self.submit = QPushButton("OK", self)
        self.grid.addWidget(self.submit, 10, 0)

        #       Action on clicking submit                 
        self.submit.clicked.connect(self.getholes)

    def getholes(self):
        memorysize    = float(self.memoryinput.text())
        numberofholes = int(self.inputholes.text())
        self.hide()                                             # --- close()
        self.window2 = Window2(memorysize, numberofholes)       # --- self
        self.window2.show()


#     second window for holes input    
class Window2(QWidget):                                         # --- QMainWindow,
    def __init__(self, memorysize, numberofholes, parent=None):
        super(Window2, self).__init__(parent)

        self.memorysize, self.numberofholes = memorysize, numberofholes
        print("memorysize=`{}`,\nnumberofholes=`{}`".format(self.memorysize, self.numberofholes))

        self.setWindowTitle("Memory 2")
        self.setGeometry(50,50,500,300)
        self.home()
        self.show()

    def home(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        print(self.numberofholes)

        for n in range (2):
            self.start_add = QLabel(self)
            self.start_add.setText("Starting Address")

            self.inputstart = QLineEdit(self)

            self.size = QLabel(self)
            self.size.setText("Size")

            self.inputsize = QLineEdit(self)

            self.grid.addWidget(self.start_add, 2*n+1, 0)
            self.grid.addWidget(self.inputstart,2*n+1, 1)
            self.grid.addWidget(self.size,      2*n+1, 2)
            self.grid.addWidget(self.inputsize, 2*n+1, 3)

if __name__ == '__main__':
     app = QApplication(sys.argv)
     main = Window()
     main.show()
     sys.exit(app.exec_())