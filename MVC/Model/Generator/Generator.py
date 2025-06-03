##################################### CLASS #############################################
################################### GENERATOR ###########################################
# CURRENT # 
# This class is designed to represent the core of the model. The generator is a software
# abstraction which keep tracks of files to use, devices to simulate and other params...
# The only three main methods that contains are pcap_simulation, stop_generator and
# run_generator. The first method simulates the traffic contained in a pcap file, the
# run_generator method is necessary to run the generator and execute the simulation of 
# a particular configuration. The stop_generator is necessary to stop the currently
# working threads and close the open connections.

import time
import threading
from Utils.NetSniffer import NetSniffer
from Utils.MalformedPacketException import MalformedPacketException
from Model.MQTT_handler.MQTT_handler import MQTT_handler
from Model.Covert.EvilTasks import EvilTasks

class Generator:

	def __init__(self, broker_address="test.mosquitto.org", port=1883, interface="en0", csv_path=None, pcap_path=None):
		
		self.broker_address = broker_address
		self.port = port
		self.interface = interface
		self.csv_path = csv_path
		self.pcap_path = pcap_path
		self.MQTT_Handler = MQTT_handler(self.broker_address, self.port)
		self.Evil_obj = EvilTasks(self.MQTT_Handler)
		self.Sniffer = NetSniffer(self.port, self.interface)
		self.devices_configs = []				#List of dictionaries for devices configs
		self.supported_protocols = {"MQTTv311":4, "MQTTv5":5}

	#Fare lettura del protocollo dal pacchetto raw, oppure amen, fa niente e il protocollo rimane fisso per la simulazione anche se non mi lascia felicio :(

	#simulation from pcap file
	def pcap_simulation(self):

		from scapy.all import rdpcap
		
		try:
			packets = rdpcap(self.pcap_path)
		except Exception as e:
			print(f"Error while pcap opening {e}")
			return None

		from scapy.contrib.mqtt import MQTT, MQTTConnect, MQTTPublish, MQTTSubscribe, MQTTDisconnect
		
		last_time = None
		active_clients = {}

		for packet in packets:

			if MQTT in packet:	#The packet is MQTT
				
				current_time = packet.time
				mqtt_layer = packet[MQTT]
				client = None
						
				try:
					if MQTTConnect in mqtt_layer:

						client =  self.MQTT_Handler.if_mqtt_connection(mqtt_layer, active_clients, protocol=packet.protolevel)

					elif MQTTPublish in mqtt_layer:
						#Retain in general is set to false
						client = self.MQTT_Handler.if_mqtt_publish(mqtt_layer, active_clients, False)

					elif MQTTSubscribe in mqtt_layer:
						#Se la connessione non è andata a buon fine allora exception
						client = self.MQTT_Handler.if_mqtt_subscription(mqtt_layer, active_clients)

					elif MQTTDisconnect in mqtt_layer:

						self.MQTT_Handler.if_mqtt_disconnection(mqtt_layer, active_clients)
				
					if last_time is not None:
					
						delay = float(current_time - last_time)
						delay = min(max(0, delay), 5.0)

						if delay > 0:
							time.sleep(delay)

					last_time = current_time

				except MalformedPacketException as e:

					continue

				except Exception as e:
					#print(f"pcap processing error {traceback.format_exc()}")
					continue
					
		print(f"Total active clients: {len(active_clients)}")

		with self.MQTT_Handler.client_lock:
			for client_id, client in list(active_clients.items()):
				
				if client.is_connected():

					client.disconnect()
					client.loop_stop()

				if client in self.MQTT_Handler.client_list:

					self.MQTT_Handler.client_list.remove(client)
	



	def get_devices_configs(self):
		
		return self.devices_configs




	def clear_devices_configs(self):
		
		self.devices_configs = None




	def add_device_config(self, config_dict):
		
		self.devices_configs.append(config_dict)



	def run_generator(self):

		#Necessary check in order to establish if the generator has the proper data to run
		#print(f"Controllo variabili: {self.csv_path, self.devices_configs}")
	
		if self.csv_path or self.devices_configs:
			
			for i, config in enumerate(self.devices_configs):
				
				role = str(config.get("Role", "")).strip().lower()
				event_type = str(config.get("Type", "")).strip().lower()
				read_protocol = str(config.get("Protocol", "MQTTv311"))	#4 -> MQTT 3.1.1, 5 -> MQTT 5
				protocol = self.supported_protocols[read_protocol]
				retain = bool(config.get("Retain", False))
				print(f"SELECTED PROTOCOL: {protocol}")

				#print(f"Config: {config}")
				### IMPORTANTE: Provare a togliere questo match case usando un dictionary e try/catch. dos, publisher, subscriber... sono le chiavi. I valori sono le corrispondenti funzioni da usare
				match role:

					case "denial of service" | "denial of service 2":

						self.Evil_obj.DoS_attack(config, protocol, retain, role)

					case "publisher":
						
						client_id = f"client_{role}_{i}"
						print(f"client_id: {client_id}")
						client = self.MQTT_Handler.mqtt_register_client(client_id, protocol=protocol)

						if event_type == "periodic":
						
							target_func = self.Evil_obj.periodic_publish
						elif event_type == "event":

							target_func = self.Evil_obj.event_publish

						if target_func:

							thread = threading.Thread(target=target_func, args=(client, config))
							#thread.daemon = True
							thread.daemon = False
							self.MQTT_Handler.working_threads.append(thread)
							thread.start()
						else:

							continue

					case "subscriber":

						client_id = f"client_{role}_{i}"
						client = self.MQTT_Handler.mqtt_register_client(client_id, protocol=protocol)
						topic = config.get("Topic")
						qos = int(config.get("QoS", 0))
						#print(f"AAAA QOS: {qos}")

						if topic:

							self.MQTT_Handler.mqtt_topic_subscription(client, topic, qos)
							
							def subscriber_loop():
								client.loop_forever()

							thread = threading.Thread(target=subscriber_loop)
							thread.daemon = False
							self.MQTT_Handler.working_threads.append(thread)
							thread.start()

						else:

							continue

					case _:

						continue
			return True

		elif self.pcap_path:

			thread = threading.Thread(target=self.pcap_simulation)
			thread.daemon = False
			self.MQTT_Handler.working_threads.append(thread)
			thread.start()
			return True



	#Stop all the working threads after 2 seconds for expired time
	def stop_generator(self):

		for thread in self.MQTT_Handler.working_threads:
			
			if thread.is_alive():

				thread.join(timeout=2.0)

		with self.MQTT_Handler.client_lock:

			clients_to_remove = list(self.MQTT_Handler.client_list)
			self.MQTT_Handler.client_list.clear()

			for client in clients_to_remove:

				client_id_string = client._client_id.decode() if client._client_id else "Unnamed"

				try:

					client.loop_stop()
					client.disconnect()
						
				except Exception as e:

					print(f"Client disconnection error: {client_id_string} : {e}")

		self.MQTT_Handler.working_threads = []

		return True