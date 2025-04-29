import pandas as pd
import numpy as np
import random, time
import argparse, base64
import os, signal, subprocess
import threading
import sys
sys.path.append("../../Utils")
sys.path.append("../MQTT_handler")	#Da cambiare nome a MQTT_handler perchè sembra un handler di controller per via del suo nome
sys.path.append("../Covert")
import NetSniffer
import MQTT_handler
import EvilTasks
from datetime import datetime

class Generator:
	
	# CLASS CONSTRUCTOR

	def __init__(self, broker_address="test.mosquitto.org", port=1883):
		
		self.broker_address = broker_address	#Broker address
		self.port = port 						#Port
		
		#Probabilmente vanno inseriti dentro MQTT_handler
		#self.client_list = []					#devices
		#self.thread_list = []					#threads linked to devices

		self.MQTT_Handler = MQTT_handler(broker_address, port)
		self.Evil_obj = EvilTasks(MQTT_Handler)
		self.Sniffer = NetSniffer(port)
		#self.capture = None						#capture process -> sostituito da NetSniffer	######OCCHIO######
		self.devices_configs = []				#List of dictionaries for devices configs




	##################################################################################################
	# PCAP REPLAY FOR MQTT TRAFFIC SIMULATION 														 #
	def pcap_simulation(self, pcap_path):
		
		try:
			packets = rdpcap(pcap_path)
		except Exception as e:
			print("Error while pcap opening")
			return None

		last_time = None
		active_clients = {}

		for packet in packets:

			if MQTT in packet:	#The packet is MQTT 
				
				current_time = packet.time
				mqtt_layer = packet[MQTT]
				client = None
						
				try:
					if MQTTConnect in mqtt_layer:

						client =  self.MQTT_Handler.if_mqtt_connection(mqtt_layer, active_clients)

					elif MQTTPublish in mqtt_layer:

						client = self.MQTT_Handler.if_mqtt_publish(mqtt_layer, active_clients)

					elif MQTTSubscribe in mqtt_layer:

						client = self.MQTT_Handler.if_mqtt_subscription(mqtt_layer, active_clients)

					elif MQTTDisconnect in mqtt_layer:

						self.MQTT_Handler.if_mqtt_disconnection(mqtt_layer, active_clients)
				
					if last_time is not None:
					
						delay = float(current_time - last_time)
						delay = min(max(0, delay), 5.0)

						if delay > 0:
							time.sleep(delay)

					last_time = current_time

				except Exception as e:
					print("pcap processing error")

		with self.MQTT_Handler.client_lock:
			for client_id, client in list(active_clients.items()):
				
				if client.is_connected():
					client.disconnect()
					client.loop_stop()

				if client in self.MQTT_Handler.client_list:
					self.MQTT_Handler.client_list.remove(client)														   #
	##################################################################################################
	

	#################################### UTILITY METHODS #######################################

	# GET DEVICES CONFIGS
	def get_devices_configs(self):
		
		return self.devices_configs

	# CLEAR DEVICES CONFIGS
	def clear_devices_configs(self):
		
		self.devices_configs = None

	# ADDS A DICTIONARY TO A LIST OF DEVICES CONFIGS
	def add_device_config(self, config_dict):
		
		self.devices_configs.append(config_dict)


	################################ RUN AND STOP GENERATOR ####################################

	def run_generator(self):
		
		
		self.Sniffer.run_tshark()

		#self.MQTT_Handler.working_threads = []

		#Faccio questo controllo perchè prima di runnare il generatore,
		#devo o caricare il file con i dati sintetici o caricare il file
		#pcap. Quindi alla fine della fiera, nel controller devo mettere
		#la logica che riempie quelle liste e poi runna il programma
		if self.csv_path and self.devices_configs:
			
			for i, config in enumerate(self.devices_configs):
				
				role = str(config.get("Role", "")).strip().lower()
				event_type = str(config.get("Type", "")).strip().lower()

				match role:

					case "dos_attack":

						self.Evil_obj.DoS_attack(config)

					case "publisher":
						
						client_id = f"client_{role}_{i}"
						client = self.MQTT_Handler.mqtt_register_client(client_id)

						if event_type == "periodic":
						
							target_func = self.Evil_obj.periodic_publish
						elif event_type == "event":

							target_func = self.event_publish

						if target_func:

							thread = threading.Thread(target=target_func, args=(client, config))
							thread.daemon = True
							self.MQTT_Handler.working_threads.append(thread)
							thread.start()
						else:

							continue

					case "subscriber":

						client_id = f"client_{role}_{i}"
						client = self.MQTT_Handler.mqtt_register_client(client_id)
						topic = config.get("Topic")
						qos = int(config.get("QoS", 0))

						if topic:

							self.MQTT_Handler.mqtt_topic_subscription(client, topic, qos)
						else:

							continue

					case _:

						continue
			
			return True

		elif self.pcap_path:

			thread = threading.Thread(target=self.pcap_simulation, args=(self.pcap_path,))
			thread.daemon = True
			self.MQTT_Handler.working_threads.append(thread)
			thread.start()
			return True

		else:

			self.Sniffer.stop_tshark()
			return False

	def stop_generator(self):
		
		#Stop all the working threads after 2 seconds for expired time

		for thread in self.MQTT_Handler.working_threads:
			
			if thread.is_alive():

				thread.join(timeout=2.0)

		with self.MQTT_Handler.client_lock:

			clients_to_remove = list(self.MQTT_Handler.client_list)
			self.MQTT_Handler.client_list.clear()

			for client in clients_to_remove:

				client_id_string = client._client_id.decode() if client._client_id else "Unnamed"

				try:
					if client.is_disconnected():

						client.disconnect()
						client.loop_stop(timeout=1.0)
					else:

						client.loop_stop(timeout=1.0)

				except Exception as e:

					print(f"Client disconnection error: {client_id_string} : {e}")

		self.Sniffer.stop_tshark()
		self.MQTT_Handler.working_threads = []

		return True