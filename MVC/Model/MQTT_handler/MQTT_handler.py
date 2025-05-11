##################################### CLASS #############################################
################################## MQTT_Handler #########################################
# CURRENT # 
# This class manages all the features necessary for MQTT protocol: publish a message,
# subscribe to a topic, check connection, create a MQTT client.

import paho.mqtt.client as mqtt
import threading
import time
from scapy.contrib.mqtt import MQTT, MQTTConnect, MQTTPublish, MQTTSubscribe
from Utils.MQTT5Parser import MQTT5Parser


class MQTT_handler:	

	def __init__(self, broker_address, port):
	
		self.broker_address = broker_address
		self.port = port
		self.client_lock = threading.Lock()		#Locks management
		self.client_list = []					#list of devices (clients)
		self.working_threads = []
		self.client_protocols = {}


	
	#Action to perform whenever a subscriber receives a message. This method is required by client object
	def on_message(self, client, userdata, message):
		
		if client._client_id:

			client_id = client._client_id.decode()
		else:

			client_id = "anonymous"

		print(f"Received message '{message.payload.decode()}' from topic '{message.topic}' (Client: '{client_id}')")



	#MQTT client creation
	def mqtt_client(self, client_id=None, timeout=10.0, protocol=mqtt.MQTTv311):
		
		try:
			client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=protocol)
			client.enable_logger()
			client.on_message = self.on_message
			client.connect(self.broker_address, port=self.port, keepalive=60)
			client.loop_start()

			while not client.is_connected() and timeout > 0:
				time.sleep(0.1)
				timeout -= 0.1

			if not client.is_connected():
				
				print(f"MQTT client {client_id} cannot establish the connection")
				return None

			return client
		
		except Exception as e:
			print("MQTT client connection error ", {e})
			return None



	#MQTT client registration: each client logs itself in thread/client list		
	def mqtt_register_client(self, client_id=None, protocol=mqtt.MQTTv311):
		
		client_id = client_id or ""
		client = self.mqtt_client(client_id=client_id, protocol=protocol)
		
		if client is not None:
		
			with self.client_lock:
				self.client_list.append(client)

			self.client_protocols[client_id] = protocol
			print(f"[DEBUG] Registrato client_id={client_id} con protocol={protocol}")
		return client



	#MQTT message publish method: return true iff the message has been sent correctly
	def mqtt_publish_msg(self, publisher, topic, qos, payload):
		
		if publisher is None or not publisher.is_connected():

			print("The publisher does not exists or it is not connected")
			return False

		try:
			
			info = publisher.publish(topic, payload, qos)
			if info.rc == mqtt.MQTT_ERR_SUCCESS:

				print("Message sent")
				return True

		except Exception as e:
			print(f"Error while sending message to {topic}: {e}")
			return False
		return False



	#MQTT topic subscription: return true iff the subscription is successful, false otherwise
	def mqtt_topic_subscription(self, subscriber, topic, qos):
		
		if subscriber is None or not subscriber.is_connected():

			print("The subscriber does not exists or it is not connected")
			return False

		try:
			print("AIUTATEMI VI PREGO")
			info, mid = subscriber.subscribe(topic, qos)
			if info == mqtt.MQTT_ERR_SUCCESS:

				print("Subscription completed")
				return True

		except Exception as e:
			print(f"subscription failed: {e}")
			return False



	#mqtt connection action
	def if_mqtt_connection(self, mqtt_layer, active_clients, protocol):
		
		raw = bytes(mqtt_layer)

		try:
			connect_info = MQTT5Parser.parse_connect_info(raw)
			protocol_level = connect_info["protocol_level"]
			client_id = MQTT5Parser.extract_client_id(raw)

		except Exception as e:
			print(f"[ERROR] Impossibile determinare protocol level o client_id: {e}")
			protocol_level = protocol
			client_id = ""

		print(f"CONNECTED WITH CLIENT_ID: {client_id}")

		if client_id not in active_clients or not active_clients.get(client_id, None) or not active_clients[client_id].is_connected():

			client = self.mqtt_register_client(client_id, protocol_level)
			if client:

				self.client_protocols[client_id] = protocol_level
				active_clients[client_id] = client
				return client
		else:

			return active_clients[client_id]



	#mqtt publishing action
	def if_mqtt_publish(self, mqtt_layer, active_clients):
		
		last_client = None

		if active_clients:

			last_client = list(active_clients.values())[-1]
			print(f"last_client {last_client}")			

		if last_client:

			client_id = last_client._client_id.decode("utf-8", errors="ignore") if last_client._client_id else ""
			protolevel = self.client_protocols.get(client_id, 4)

			print(f"[DEBUG] Protocol map: {self.client_protocols}")
			print(f"[DEBUG] Protocol for '{client_id}': {protolevel}")

			if protolevel == 5:

				print("[INFO] MQTT 5 detected: parsing publish manually")
				raw_bytes = bytes(mqtt_layer)

				try:
					topic, qos, payload = MQTT5Parser.parse_publish_payload(raw_bytes)
					print(f"[PARSED MQTT 5 PUBLISH] topic: {topic}, qos: {qos}, payload: {payload}")
				except Exception as e:
					print(f"[ERROR] Failed to parse MQTT 5 PUBLISH payload: {e}")
					return None
			else:

				mqtt_publish = mqtt_layer[MQTTPublish]
				topic = mqtt_publish.topic.decode("utf-8", errors="ignore")
				qos = mqtt_layer.QOS
				payload = mqtt_publish.value
				print(f"[WARNING] Using scapy value: {payload}")

			self.mqtt_publish_msg(last_client, topic, qos, payload)
			print(f"Pubblico su Topic' {topic} con payload {payload}")
			return last_client

		return None





	#mqtt subscription action -> prints are kept for debugging
	def if_mqtt_subscription(self, mqtt_layer, active_clients):
		
		subscriber = None

		if active_clients:
			
			subscriber = list(active_clients.values())[-1]

		if subscriber:
			
			client_id = subscriber._client_id.decode("utf-8", errors="ignore") if subscriber._client_id else ""
			protolevel = self.client_protocols.get(client_id, 4)	#default case MQTT3.1.1
			
			if protolevel == 5:

				print("[INFO] MQTT5 detected: using custom parser")
				raw_bytes = bytes(mqtt_layer)
				try:
					packet_id, topics = MQTT5Parser.parse_subscribe_payload(raw_bytes)

					for topic, qos in topics:
						print(f"[PARSED MQTT 5] topic: {topic}, qos: {qos}")
						self.mqtt_topic_subscription(subscriber, topic, qos)

				except Exception as e:
					print(f"[ERROR] Failed to parse MQTT 5 payload: {e}")

			else:

				print("[INFO] MQTT 3.x detected: using Scapy parsing")

				mqtt_subscribe = mqtt_layer[MQTTSubscribe]

				if hasattr(mqtt_subscribe, "topics") and isinstance(mqtt_subscribe.topics, list):

					for entry in mqtt_subscribe.topics:
						if isinstance(entry, (tuple, list)) and len(entry) == 2:

							raw_topic, qos_val = entry

							if isinstance(raw_topic, bytes):

								topic = raw_topic.decode("utf-8", errors="ignore")
							elif isinstance(raw_topic, str):

								topic = raw_topic
							else:

								topic = bytes(raw_topic).decode("utf-8", errors="ignore")

							qos = int(qos_val)
							print(f"Quality of service subscriber: {qos}")
							self.mqtt_topic_subscription(subscriber, topic, qos)
						else:
							
							print(f"[WARNING] Unexpected subscription entry format: {entry}")
				else:

					print("[ERROR] MQTTSubscribe.topics is missing or malformed")


			return subscriber

		return None



	#mqtt disconnection action
	def if_mqtt_disconnection(self, mqtt_layer, active_clients):
		
		if active_clients:
			
			last_client_id = list(active_clients.keys())[-1]
			client_to_disconnect = active_clients.pop(last_client_id, None)

			if client_to_disconnect:

				with self.client_lock:
					if client_to_disconnect in self.client_list:

						self.client_list.remove(client_to_disconnect)
					client_to_disconnect.disconnect()
					client_to_disconnect.loop_stop()