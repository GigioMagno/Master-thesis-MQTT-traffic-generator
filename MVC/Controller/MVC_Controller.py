from Controller.Handlers.Configs_Handler import Configs_Handler
from View.main_window import MainWindow
import time

class MVC_Controller(object):

	#Generator e View sono passate dal modello
	def __init__(self, Gen, View):
		self.Gen = Gen
		self.View = View
		
		#Handler for commands load/store configs
		self.Configs_handler = Configs_Handler(self.Gen, self.View)	
		self.build()


	def start_gen(self):
		if self.Gen.pcap_path is None:
		
			self.Gen.Sniffer.run_tshark()
			time.sleep(3)	#3 secondi per avvio di tshark (più che sufficienti)
			print("Devices = ", len(self.Gen.devices_configs))
			self.Gen.run_generator()

		elif self.Gen.pcap_path is not None:

			self.Gen.run_generator()

			


	def stop_gen(self):
		self.Gen.stop_generator()
		if self.Gen.pcap_path is None:
			
			time.sleep(3)
			self.Gen.Sniffer.stop_tshark()

		self.Gen.devices_configs = []
		self.Gen.pcap_path = None
		self.Gen.csv_path = None
		print("Generator stopped")


	def build(self):	#links view and domain
		self.View.load_csv.clicked.connect(self.Configs_handler.read_from_csv_action)
		self.View.save_to_csv.clicked.connect(self.Configs_handler.save_to_csv_actions)
		self.View.add_config.clicked.connect(self.Configs_handler.add_config_actions)
		self.View.empirical_config.browse_button.clicked.connect(self.Configs_handler.read_from_pcap_action)
		self.View.run_gen.clicked.connect(self.start_gen)
		self.View.stop_gen.clicked.connect(self.stop_gen)


#Conviene fare in modo che quando cambio 
#pagina resetto i path e svuoto le strutture dati		