import sys
import time
from PyQt4 import QtGui
sys.path.append('C:\\Users\\LitePlacer\\Documents\\liteplacer-glue')

class Test():
	'''
	Mother class for test objects
	Defines a test to be executed by the GLUI 
	Provides a way to specify the inputs
	'''
	def __init__(self, main_window, GUI):
		self.main_window = main_window
		self.GUI = GUI
		# var_dict should contain 'var_name': {'type': str/float/int/..., 'val': None} 
		self.var_dict = {}
	
	def set_var(self):
		for var_name in self.var_dict:
			text, ok = QtGui.QInputDialog.getText(self.main_window, 'Input Dialog: '+var_name, 'Enter '+var_name+':')
			try:
			    self.var_dict[var_name]['val'] = self.var_dict[var_name]['type'](text)
			except:
				self.var_dict[var_name]['val'] = self.var_dict[var_name]['type'](text)
			print(self.var_dict)
	
	def run(self):
		print "this should be overwritten"