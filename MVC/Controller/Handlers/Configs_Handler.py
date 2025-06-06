##################################### CLASS #############################################
################################ CONFIGS_HANDLER ########################################
# CURRENT # 
# This handler manages the actions performed by the buttons of the view for the
# management of loading and saving configs. The main implemented functions allow to 
# read a pcap file, read a csv file, save a csv file and add a single device 
# configuration.
# This class is a further abstraction respect to IO_Handler. This class manages both view
# and lower level features, but low level features are directly managed by IO_Handler

from Controller.Handlers.IO_Handler import IO_Handler




class Configs_Handler(object):
	
	def __init__(self, Gen, View):
		
		self.Gen = Gen
		self.View = View
		self.IO_handler = IO_Handler(self.Gen)




	def read_from_csv_action(self):

		from PyQt5.QtWidgets import QFileDialog

		csv_path, _ = QFileDialog.getOpenFileName(self.View, "Open csv File", "", "csv Files (*.csv);; All Files (*)")
		if csv_path:

			self.IO_handler.load_from_csv_devices_configs(csv_path)
			self.Gen.csv_path = csv_path
			print("csv correctly loaded")
		else:

			print("no csv file loaded")




	def save_to_csv_actions(self):

		from PyQt5.QtWidgets import QFileDialog
		from datetime import datetime
		import os

		directory = QFileDialog.getExistingDirectory()
		if directory:

			timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
			csv_path = os.path.join(directory, f"export_{timestamp}.csv")
			self.IO_handler.save_in_csv_devices_configs(csv_path)




	def add_config_actions(self):
		
		selected_role = self.View.manual_config.role_selector.currentText()
		config = self.empty_config_dict()

		if selected_role == "Publisher":

			try:
				config["Topic"] = self.View.manual_config.publisher_config.topic_input.text()
				device_timing = self.View.manual_config.publisher_config.device_timing_selector.currentText()
				config["Type"] = device_timing
				config["QoS"] = int(self.View.manual_config.publisher_config.qos_selector.currentText())
				config["Payload"] = self.View.manual_config.publisher_config.payload_input.text()
				config["Role"] = selected_role
				config["Retain"] = self.View.manual_config.publisher_config.retain_selector.currentData()

				if device_timing == "Event":
				
					config["MinRange"] = self.View.manual_config.publisher_config.min_time_input.value()
					config["MaxRange"] = self.View.manual_config.publisher_config.max_time_input.value()
			
				elif device_timing == "Periodic":
				
					config["Period"] = self.View.manual_config.publisher_config.period_input.value()

				config["Distribution"] = self.View.manual_config.publisher_config.distribution_selector.currentText()
				device_type = self.View.manual_config.publisher_config.device_type_selector.currentText()
				config["DeviceType"] = device_type
				if device_type == "Counterfeit":
				
					config["HiddenMessage"] = self.View.manual_config.publisher_config.hidden_message_input.text()
					config["EmbeddingMethod"] = self.View.manual_config.publisher_config.embedding_method_selector.currentText()

				self.clear_fields_publisher()
				print("Publisher configuration added!")

			except Exception as e:
				print(f"Publisher: {e}")

		elif selected_role == "Subscriber":

			try:
				config["Topic"] = self.View.manual_config.subscriber_config.topic_input.text()
				config["QoS"] = self.View.manual_config.subscriber_config.qos_selector.currentText()
				config["Role"] = selected_role

				self.clear_fields_subscriber()
				print("Subscriber configuration added!")

			except Exception as e:
				print(f"Subscriber: {e}")

		elif selected_role == "Denial of Service":
			
			try:
				config["Topic"] = self.View.manual_config.dos_config.topic_input.text()
				config["QoS"] = self.View.manual_config.dos_config.qos_selector.currentText()
				config["Payload"] = self.View.manual_config.dos_config.payload_input.text()
				#config["Payload"] = self.View.manual_config.dos_config.payload_input.toPlainText()
				device_timing = self.View.manual_config.dos_config.device_timing_selector.currentText()
				config["Type"] = device_timing
				config["NumClients"] = self.View.manual_config.dos_config.num_clients_input.value()
				config["Duration"] = self.View.manual_config.dos_config.duration_input.value()
				config["Role"] = selected_role
				config["Period"] = self.View.manual_config.dos_config.period_input.value()
				config["Retain"] = self.View.manual_config.dos_config.retain_selector.currentData()

				self.clear_fields_dos()
				print("Denial of Service configuration added!")
				
			except Exception as e:
				print(f"Denial of Service: {e}")

		config["Protocol"] = self.View.manual_config.protocol_selector.currentText()
		#protocol = self.View.manual_config.protocol_selector.currentText()
		#config["Protocol"] = protocol
		#print(f"IL PROTOCOLLO USATO È: {protocol}")
		self.Gen.add_device_config(config)	#Tolta da publisher, subscriber, DOS


	def empty_config_dict(self):
		
		config = {}
		config["Topic"] = None
		config["Type"] = None
		config["QoS"] = None
		config["Payload"] = None
		config["Period"] = None
		config["MinRange"] = None
		config["MaxRange"] = None
		config["Distribution"] = None
		config["DeviceType"] = None
		config["HiddenMessage"] = None
		config["EmbeddingMethod"] = None
		config["NumClients"] = None
		config["Duration"] = None
		config["Role"] = None
		config["Protocol"] = None
		return config




	def clear_fields_publisher(self):
		
		self.View.manual_config.publisher_config.topic_input.clear()
		self.View.manual_config.publisher_config.qos_selector.setCurrentIndex(0)
		self.View.manual_config.publisher_config.payload_input.clear()
		self.View.manual_config.publisher_config.device_timing_selector.setCurrentIndex(0)
		self.View.manual_config.publisher_config.min_time_input.setValue(0.0)
		self.View.manual_config.publisher_config.max_time_input.setValue(0.0)
		self.View.manual_config.publisher_config.period_input.setValue(0.0)
		self.View.manual_config.publisher_config.distribution_selector.setCurrentIndex(0)
		self.View.manual_config.publisher_config.device_type_selector.setCurrentIndex(0)
		self.View.manual_config.publisher_config.hidden_message_input.clear()
		self.View.manual_config.publisher_config.embedding_method_selector.setCurrentIndex(0)




	def clear_fields_subscriber(self):
		
		self.View.manual_config.subscriber_config.topic_input.clear()
		self.View.manual_config.subscriber_config.qos_selector.setCurrentIndex(0)




	def clear_fields_dos(self):
		
		self.View.manual_config.dos_config.topic_input.clear()
		self.View.manual_config.dos_config.qos_selector.setCurrentIndex(0)
		self.View.manual_config.dos_config.payload_input.clear()
		self.View.manual_config.dos_config.device_timing_selector.setCurrentIndex(0)
		self.View.manual_config.dos_config.period_input.setValue(0.0)
		self.View.manual_config.dos_config.num_clients_input.setValue(0)
		self.View.manual_config.dos_config.duration_input.setValue(0.0)




	def read_from_pcap_action(self):
		
		pcap_path, _ = QFileDialog.getOpenFileName(self.View, "Open pcap File", "", "pcap Files (*.pcap);; All Files (*)")
		if pcap_path is not None:
			
			self.Gen.pcap_path = pcap_path
			self.Gen.devices_configs = []
			self.View.empirical_config.file_label.setText(f"{pcap_path}")
			print(f"pcap_path: {pcap_path}")
		else:
			
			pcap_path = None
			print("No pcap file loaded")