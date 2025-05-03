from Controller.Handlers.Configs_Handler import Configs_Handler
from View.main_window import MainWindow


class MVC_Controller(object):

	#Generator e View sono passate dal modello
	def __init__(self, Gen, View):
		self.Gen = Gen
		self.View = View
		
		self.Configs_handler = Configs_Handler(self.Gen, self.View)	#Handler for commands load/store configs
		self.build()

	#def save_to_csv_action(self):
		#self.Gen.csv_path






	def build(self):	#links view and domain
		self.View.load_csv.clicked.connect(self.Configs_handler.read_from_csv_action)
		self.View.save_to_csv.clicked.connect(self.Configs_handler.save_to_csv_actions)
		self.View.add_config.clicked.connect(self.Configs_handler.add_config_actions)