from Controller.Handlers.IO_Handler import IO_Handler
from View.main_window import MainWindow
from PyQt5.QtWidgets import QFileDialog

class MVC_Controller(object):

	#Generator e View sono passate dal modello
	def __init__(self, Gen, View):
		self.Gen = Gen
		self.View = View

		self.IO_handler = IO_Handler(self.Gen)	#Handler for IO management
		self.build()
		
	#def save_to_csv_action(self):
		#self.Gen.csv_path

	def read_from_csv_action(self):
		csv_path, _ = QFileDialog.getOpenFileName(self.View, "Open csv File", "", "csv Files (*.csv);; All Files (*)")
		print(csv_path)
		if csv_path:
			self.IO_handler.load_from_csv_devices_configs(csv_path)
			print("csv correctly loaded")
		else:
			print("no csv file loaded")


	def build(self):	#links view and domain
		self.View.load_csv.clicked.connect(self.read_from_csv_action)